import librosa
import numpy as np
import os
import requests
import shutil
import soundfile as sf
import torch
import torch.nn as nn
import torch.nn.functional as F

from shttst.audio.utils import convert_to_mono_channel, save_audio
from zipfile import ZipFile

CHECKPOINT_CACHE_PATH = os.path.expanduser('~/.cache/shttst/vocal_remover/baseline.pth')
ZIP_PATH = os.path.expanduser('~/.cache/shttst/vocal_remover/vr.zip')

def get_checkpoint():
    if not os.path.exists(CHECKPOINT_CACHE_PATH):
        os.makedirs(os.path.dirname(CHECKPOINT_CACHE_PATH), exist_ok=True)
        resp = requests.get('https://github.com/tsurumeso/vocal-remover/releases/download/v5.0.3/vocal-remover-v5.0.3.zip')
        with open(ZIP_PATH, 'w+b') as fs:
            fs.write(resp.content)
        with ZipFile(ZIP_PATH, 'r') as zipped_vr:
            zipped_vr.extract('vocal-remover/models/baseline.pth', os.path.dirname(CHECKPOINT_CACHE_PATH))
            
        shutil.move(os.path.join(os.path.dirname(CHECKPOINT_CACHE_PATH), 'vocal-remover/models/baseline.pth'), CHECKPOINT_CACHE_PATH)
        shutil.rmtree(os.path.join(os.path.dirname(CHECKPOINT_CACHE_PATH), 'vocal-remover'), ignore_errors=False, onerror=None)
        os.remove(ZIP_PATH)

    return CHECKPOINT_CACHE_PATH

# Taken from: https://github.com/tsurumeso/vocal-remover/
def make_padding(width, cropsize, offset):
    left = offset
    roi_size = cropsize - offset * 2
    if roi_size == 0:
        roi_size = cropsize
    right = roi_size - (width % roi_size) + left

    return left, right, roi_size

def crop_center(h1, h2):
    h1_shape = h1.size()
    h2_shape = h2.size()

    if h1_shape[3] == h2_shape[3]:
        return h1
    elif h1_shape[3] < h2_shape[3]:
        raise ValueError('h1_shape[3] must be greater than h2_shape[3]')

    # s_freq = (h2_shape[2] - h1_shape[2]) // 2
    # e_freq = s_freq + h1_shape[2]
    s_time = (h1_shape[3] - h2_shape[3]) // 2
    e_time = s_time + h2_shape[3]
    h1 = h1[:, :, :, s_time:e_time]

    return h1


def wave_to_spectrogram(wave, hop_length, n_fft):
    wave_left = np.asfortranarray(wave[0])
    wave_right = np.asfortranarray(wave[1])

    spec_left = librosa.stft(wave_left, n_fft=n_fft, hop_length=hop_length)
    spec_right = librosa.stft(wave_right, n_fft=n_fft, hop_length=hop_length)
    spec = np.asfortranarray([spec_left, spec_right])

    return spec


def spectrogram_to_image(spec, mode='magnitude'):
    if mode == 'magnitude':
        if np.iscomplexobj(spec):
            y = np.abs(spec)
        else:
            y = spec
        y = np.log10(y ** 2 + 1e-8)
    elif mode == 'phase':
        if np.iscomplexobj(spec):
            y = np.angle(spec)
        else:
            y = spec

    y -= y.min()
    y *= 255 / y.max()
    img = np.uint8(y)

    if y.ndim == 3:
        img = img.transpose(1, 2, 0)
        img = np.concatenate([
            np.max(img, axis=2, keepdims=True), img
        ], axis=2)

    return img


def aggressively_remove_vocal(X, y, weight):
    X_mag = np.abs(X)
    y_mag = np.abs(y)
    # v_mag = np.abs(X_mag - y_mag)
    v_mag = X_mag - y_mag
    v_mag *= v_mag > y_mag

    y_mag = np.clip(y_mag - v_mag * weight, 0, np.inf)

    return y_mag * np.exp(1.j * np.angle(y))


def merge_artifacts(y_mask, thres=0.05, min_range=64, fade_size=32):
    if min_range < fade_size * 2:
        raise ValueError('min_range must be >= fade_size * 2')

    idx = np.where(y_mask.min(axis=(0, 1)) > thres)[0]
    start_idx = np.insert(idx[np.where(np.diff(idx) != 1)[0] + 1], 0, idx[0])
    end_idx = np.append(idx[np.where(np.diff(idx) != 1)[0]], idx[-1])
    artifact_idx = np.where(end_idx - start_idx > min_range)[0]
    weight = np.zeros_like(y_mask)
    if len(artifact_idx) > 0:
        start_idx = start_idx[artifact_idx]
        end_idx = end_idx[artifact_idx]
        old_e = None
        for s, e in zip(start_idx, end_idx):
            if old_e is not None and s - old_e < fade_size:
                s = old_e - fade_size * 2

            if s != 0:
                weight[:, :, s:s + fade_size] = np.linspace(0, 1, fade_size)
            else:
                s -= fade_size

            if e != y_mask.shape[2]:
                weight[:, :, e - fade_size:e] = np.linspace(1, 0, fade_size)
            else:
                e += fade_size

            weight[:, :, s + fade_size:e - fade_size] = 1
            old_e = e

    v_mask = 1 - y_mask
    y_mask += weight * v_mask

    return y_mask


def align_wave_head_and_tail(a, b, sr):
    a, _ = librosa.effects.trim(a)
    b, _ = librosa.effects.trim(b)

    a_mono = a[:, :sr * 4].sum(axis=0)
    b_mono = b[:, :sr * 4].sum(axis=0)

    a_mono -= a_mono.mean()
    b_mono -= b_mono.mean()

    offset = len(a_mono) - 1
    delay = np.argmax(np.correlate(a_mono, b_mono, 'full')) - offset

    if delay > 0:
        a = a[:, delay:]
    else:
        b = b[:, np.abs(delay):]

    if a.shape[1] < b.shape[1]:
        b = b[:, :a.shape[1]]
    else:
        a = a[:, :b.shape[1]]

    return a, b


def cache_or_load(mix_path, inst_path, sr, hop_length, n_fft):
    mix_basename = os.path.splitext(os.path.basename(mix_path))[0]
    inst_basename = os.path.splitext(os.path.basename(inst_path))[0]

    cache_dir = 'sr{}_hl{}_nf{}'.format(sr, hop_length, n_fft)
    mix_cache_dir = os.path.join(os.path.dirname(mix_path), cache_dir)
    inst_cache_dir = os.path.join(os.path.dirname(inst_path), cache_dir)
    os.makedirs(mix_cache_dir, exist_ok=True)
    os.makedirs(inst_cache_dir, exist_ok=True)

    mix_cache_path = os.path.join(mix_cache_dir, mix_basename + '.npy')
    inst_cache_path = os.path.join(inst_cache_dir, inst_basename + '.npy')

    if os.path.exists(mix_cache_path) and os.path.exists(inst_cache_path):
        X = np.load(mix_cache_path)
        y = np.load(inst_cache_path)
    else:
        X, _ = librosa.load(
            mix_path, sr=sr, mono=False, dtype=np.float32, res_type='kaiser_fast')
        y, _ = librosa.load(
            inst_path, sr=sr, mono=False, dtype=np.float32, res_type='kaiser_fast')

        X, y = align_wave_head_and_tail(X, y, sr)

        X = wave_to_spectrogram(X, hop_length, n_fft)
        y = wave_to_spectrogram(y, hop_length, n_fft)

        np.save(mix_cache_path, X)
        np.save(inst_cache_path, y)

    return X, y, mix_cache_path, inst_cache_path


def spectrogram_to_wave(spec, hop_length=1024):
    if spec.ndim == 2:
        wave = librosa.istft(spec, hop_length=hop_length)
    elif spec.ndim == 3:
        spec_left = np.asfortranarray(spec[0])
        spec_right = np.asfortranarray(spec[1])

        wave_left = librosa.istft(spec_left, hop_length=hop_length)
        wave_right = librosa.istft(spec_right, hop_length=hop_length)
        wave = np.asfortranarray([wave_left, wave_right])

    return wave

class Encoder(nn.Module):

    def __init__(self, nin, nout, ksize=3, stride=1, pad=1, activ=nn.LeakyReLU):
        super(Encoder, self).__init__()
        self.conv1 = Conv2DBNActiv(nin, nout, ksize, stride, pad, activ=activ)
        self.conv2 = Conv2DBNActiv(nout, nout, ksize, 1, pad, activ=activ)

    def __call__(self, x):
        h = self.conv1(x)
        h = self.conv2(h)

        return h


class Decoder(nn.Module):
    def __init__(self, nin, nout, ksize=3, stride=1, pad=1, activ=nn.ReLU, dropout=False):
        super(Decoder, self).__init__()
        self.conv1 = Conv2DBNActiv(nin, nout, ksize, 1, pad, activ=activ)
        # self.conv2 = Conv2DBNActiv(nout, nout, ksize, 1, pad, activ=activ)
        self.dropout = nn.Dropout2d(0.1) if dropout else None

    def __call__(self, x, skip=None):
        x = F.interpolate(x, scale_factor=2, mode='bilinear', align_corners=True)

        if skip is not None:
            skip = crop_center(skip, x)
            x = torch.cat([x, skip], dim=1)

        h = self.conv1(x)
        # h = self.conv2(h)

        if self.dropout is not None:
            h = self.dropout(h)

        return h


class ASPPModule(nn.Module):

    def __init__(self, nin, nout, dilations=(4, 8, 12), activ=nn.ReLU, dropout=False):
        super(ASPPModule, self).__init__()
        self.conv1 = nn.Sequential(
            nn.AdaptiveAvgPool2d((1, None)),
            Conv2DBNActiv(nin, nout, 1, 1, 0, activ=activ)
        )
        self.conv2 = Conv2DBNActiv(
            nin, nout, 1, 1, 0, activ=activ
        )
        self.conv3 = Conv2DBNActiv(
            nin, nout, 3, 1, dilations[0], dilations[0], activ=activ
        )
        self.conv4 = Conv2DBNActiv(
            nin, nout, 3, 1, dilations[1], dilations[1], activ=activ
        )
        self.conv5 = Conv2DBNActiv(
            nin, nout, 3, 1, dilations[2], dilations[2], activ=activ
        )
        self.bottleneck = Conv2DBNActiv(
            nout * 5, nout, 1, 1, 0, activ=activ
        )
        self.dropout = nn.Dropout2d(0.1) if dropout else None

    def forward(self, x):
        _, _, h, w = x.size()
        feat1 = F.interpolate(self.conv1(x), size=(h, w), mode='bilinear', align_corners=True)
        feat2 = self.conv2(x)
        feat3 = self.conv3(x)
        feat4 = self.conv4(x)
        feat5 = self.conv5(x)
        out = torch.cat((feat1, feat2, feat3, feat4, feat5), dim=1)
        out = self.bottleneck(out)

        if self.dropout is not None:
            out = self.dropout(out)

        return out


class LSTMModule(nn.Module):

    def __init__(self, nin_conv, nin_lstm, nout_lstm):
        super(LSTMModule, self).__init__()
        self.conv = Conv2DBNActiv(nin_conv, 1, 1, 1, 0)
        self.lstm = nn.LSTM(
            input_size=nin_lstm,
            hidden_size=nout_lstm // 2,
            bidirectional=True
        )
        self.dense = nn.Sequential(
            nn.Linear(nout_lstm, nin_lstm),
            nn.BatchNorm1d(nin_lstm),
            nn.ReLU()
        )

    def forward(self, x):
        N, _, nbins, nframes = x.size()
        h = self.conv(x)[:, 0]  # N, nbins, nframes
        h = h.permute(2, 0, 1)  # nframes, N, nbins
        h, _ = self.lstm(h)
        h = self.dense(h.reshape(-1, h.size()[-1]))  # nframes * N, nbins
        h = h.reshape(nframes, N, 1, nbins)
        h = h.permute(1, 2, 3, 0)

        return h
    
class Conv2DBNActiv(nn.Module):

    def __init__(self, nin, nout, ksize=3, stride=1, pad=1, dilation=1, activ=nn.ReLU):
        super(Conv2DBNActiv, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(
                nin, nout,
                kernel_size=ksize,
                stride=stride,
                padding=pad,
                dilation=dilation,
                bias=False
            ),
            nn.BatchNorm2d(nout),
            activ()
        )

    def __call__(self, x):
        return self.conv(x)

class BaseNet(nn.Module):

    def __init__(self, nin, nout, nin_lstm, nout_lstm, dilations=((4, 2), (8, 4), (12, 6))):
        super(BaseNet, self).__init__()
        self.enc1 = Conv2DBNActiv(nin, nout, 3, 1, 1)
        self.enc2 = Encoder(nout, nout * 2, 3, 2, 1)
        self.enc3 = Encoder(nout * 2, nout * 4, 3, 2, 1)
        self.enc4 = Encoder(nout * 4, nout * 6, 3, 2, 1)
        self.enc5 = Encoder(nout * 6, nout * 8, 3, 2, 1)

        self.aspp = ASPPModule(nout * 8, nout * 8, dilations, dropout=True)

        self.dec4 = Decoder(nout * (6 + 8), nout * 6, 3, 1, 1)
        self.dec3 = Decoder(nout * (4 + 6), nout * 4, 3, 1, 1)
        self.dec2 = Decoder(nout * (2 + 4), nout * 2, 3, 1, 1)
        self.lstm_dec2 = LSTMModule(nout * 2, nin_lstm, nout_lstm)
        self.dec1 = Decoder(nout * (1 + 2) + 1, nout * 1, 3, 1, 1)

    def __call__(self, x):
        e1 = self.enc1(x)
        e2 = self.enc2(e1)
        e3 = self.enc3(e2)
        e4 = self.enc4(e3)
        e5 = self.enc5(e4)

        h = self.aspp(e5)

        h = self.dec4(h, e4)
        h = self.dec3(h, e3)
        h = self.dec2(h, e2)
        h = torch.cat([h, self.lstm_dec2(h)], dim=1)
        h = self.dec1(h, e1)

        return h
    
class CascadedNet(nn.Module):

    def __init__(self, n_fft, nout=32, nout_lstm=128):
        super(CascadedNet, self).__init__()
        self.max_bin = n_fft // 2
        self.output_bin = n_fft // 2 + 1
        self.nin_lstm = self.max_bin // 2
        self.offset = 64

        self.stg1_low_band_net = nn.Sequential(
            BaseNet(2, nout // 2, self.nin_lstm // 2, nout_lstm),
            Conv2DBNActiv(nout // 2, nout // 4, 1, 1, 0)
        )
        self.stg1_high_band_net = BaseNet(
            2, nout // 4, self.nin_lstm // 2, nout_lstm // 2
        )

        self.stg2_low_band_net = nn.Sequential(
            BaseNet(nout // 4 + 2, nout, self.nin_lstm // 2, nout_lstm),
            Conv2DBNActiv(nout, nout // 2, 1, 1, 0)
        )
        self.stg2_high_band_net = BaseNet(
            nout // 4 + 2, nout // 2, self.nin_lstm // 2, nout_lstm // 2
        )

        self.stg3_full_band_net = BaseNet(
            3 * nout // 4 + 2, nout, self.nin_lstm, nout_lstm
        )

        self.out = nn.Conv2d(nout, 2, 1, bias=False)
        self.aux_out = nn.Conv2d(3 * nout // 4, 2, 1, bias=False)

    def forward(self, x):
        x = x[:, :, :self.max_bin]

        bandw = x.size()[2] // 2
        l1_in = x[:, :, :bandw]
        h1_in = x[:, :, bandw:]
        l1 = self.stg1_low_band_net(l1_in)
        h1 = self.stg1_high_band_net(h1_in)
        aux1 = torch.cat([l1, h1], dim=2)

        l2_in = torch.cat([l1_in, l1], dim=1)
        h2_in = torch.cat([h1_in, h1], dim=1)
        l2 = self.stg2_low_band_net(l2_in)
        h2 = self.stg2_high_band_net(h2_in)
        aux2 = torch.cat([l2, h2], dim=2)

        f3_in = torch.cat([x, aux1, aux2], dim=1)
        f3 = self.stg3_full_band_net(f3_in)

        mask = torch.sigmoid(self.out(f3))
        mask = F.pad(
            input=mask,
            pad=(0, 0, 0, self.output_bin - mask.size()[2]),
            mode='replicate'
        )

        if self.training:
            aux = torch.cat([aux1, aux2], dim=1)
            aux = torch.sigmoid(self.aux_out(aux))
            aux = F.pad(
                input=aux,
                pad=(0, 0, 0, self.output_bin - aux.size()[2]),
                mode='replicate'
            )
            return mask, aux
        else:
            return mask

    def predict_mask(self, x):
        mask = self.forward(x)

        if self.offset > 0:
            mask = mask[:, :, :, self.offset:-self.offset]
            assert mask.size()[3] > 0

        return mask

    def predict(self, x):
        mask = self.forward(x)
        pred_mag = x * mask

        if self.offset > 0:
            pred_mag = pred_mag[:, :, :, self.offset:-self.offset]
            assert pred_mag.size()[3] > 0

        return pred_mag
    
class Separator(object):
    def __init__(self, model, device, batchsize, cropsize, postprocess=False):
        self.model = model
        self.offset = model.offset
        self.device = device
        self.batchsize = batchsize
        self.cropsize = cropsize
        self.postprocess = postprocess

    def _separate(self, X_mag_pad, roi_size):
        X_dataset = []
        patches = (X_mag_pad.shape[2] - 2 * self.offset) // roi_size
        for i in range(patches):
            start = i * roi_size
            X_mag_crop = X_mag_pad[:, :, start:start + self.cropsize]
            X_dataset.append(X_mag_crop)

        X_dataset = np.asarray(X_dataset)

        self.model.eval()
        with torch.no_grad():
            mask = []
            # To reduce the overhead, dataloader is not used.
            for i in range(0, patches, self.batchsize):
                X_batch = X_dataset[i: i + self.batchsize]
                X_batch = torch.from_numpy(X_batch).to(self.device)

                pred = self.model.predict_mask(X_batch)

                pred = pred.detach().cpu().numpy()
                pred = np.concatenate(pred, axis=2)
                mask.append(pred)

            mask = np.concatenate(mask, axis=2)

        return mask

    def _preprocess(self, X_spec):
        X_mag = np.abs(X_spec)
        X_phase = np.angle(X_spec)

        return X_mag, X_phase

    def _postprocess(self, mask, X_mag, X_phase):
        if self.postprocess:
            mask = merge_artifacts(mask)

        y_spec = mask * X_mag * np.exp(1.j * X_phase)
        v_spec = (1 - mask) * X_mag * np.exp(1.j * X_phase)

        return y_spec, v_spec

    def separate(self, X_spec):
        X_mag, X_phase = self._preprocess(X_spec)

        n_frame = X_mag.shape[2]
        pad_l, pad_r, roi_size = make_padding(n_frame, self.cropsize, self.offset)
        X_mag_pad = np.pad(X_mag, ((0, 0), (0, 0), (pad_l, pad_r)), mode='constant')
        X_mag_pad /= X_mag_pad.max()

        mask = self._separate(X_mag_pad, roi_size)
        mask = mask[:, :, :n_frame]

        y_spec, v_spec = self._postprocess(mask, X_mag, X_phase)

        return y_spec, v_spec

    def separate_tta(self, X_spec):
        X_mag, X_phase = self._preprocess(X_spec)

        n_frame = X_mag.shape[2]
        pad_l, pad_r, roi_size = make_padding(n_frame, self.cropsize, self.offset)
        X_mag_pad = np.pad(X_mag, ((0, 0), (0, 0), (pad_l, pad_r)), mode='constant')
        X_mag_pad /= X_mag_pad.max()

        mask = self._separate(X_mag_pad, roi_size)

        pad_l += roi_size // 2
        pad_r += roi_size // 2
        X_mag_pad = np.pad(X_mag, ((0, 0), (0, 0), (pad_l, pad_r)), mode='constant')
        X_mag_pad /= X_mag_pad.max()

        mask_tta = self._separate(X_mag_pad, roi_size)
        mask_tta = mask_tta[:, :, roi_size // 2:]
        mask = (mask[:, :, :n_frame] + mask_tta[:, :, :n_frame]) * 0.5

        y_spec, v_spec = self._postprocess(mask, X_mag, X_phase)

        return y_spec, v_spec


class ShmartVocalRemover():
    def __init__(self, crop_size=256, post_process=False) -> None:
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

        model = CascadedNet(2048, 32, 128)
        model.load_state_dict(torch.load(get_checkpoint(), map_location='cpu'))
        model.to(self.device)

        self.model = model
        self.sp = Separator(self.model, self.device, 1, crop_size, post_process)

    def __call__(self, wav_path, tta=False, hop_length=1024, sr=22050):
        X, sr = librosa.load(wav_path, sr=sr, mono=False, dtype=np.float32, res_type='kaiser_fast')

        if X.ndim == 1:
            X = np.asarray([X, X])

        X_spec = wave_to_spectrogram(X, hop_length, 2048)

        if tta:
            y_spec, v_spec = self.sp.separate_tta(X_spec)
        else:
            y_spec, v_spec = self.sp.separate(X_spec)

        vocals_wave = torch.from_numpy(spectrogram_to_wave(v_spec, hop_length=hop_length))
        instruments_wave = torch.from_numpy(spectrogram_to_wave(y_spec, hop_length=hop_length))

        return convert_to_mono_channel(vocals_wave), convert_to_mono_channel(instruments_wave)

if __name__ == '__main__':
    vocals, instruments = ShmartVocalRemover(post_process=True)('/content/todo/polityka/wavs/PLU2F56rqTGpucn_AI90RYWNAYTdUX_xg0_0065_15.wav')
    save_audio('/content/vr/vocals.wav', vocals)