import copy
import hashlib
import json
import librosa
import numpy as np
import os
import pathlib
import requests
import shutil
import soundfile as sf
import threading
import torch
import torch.nn as nn
import torch.nn.functional as F

from shttst.audio.utils import convert_to_mono_channel, save_audio
from zipfile import ZipFile

CHECKPOINT_CACHE_PATH = os.path.expanduser(
    "~/.cache/shttst/ultimate_vocal_remover/Vocal_HP_4BAND_3090.pth"
)
ZIP_PATH = os.path.expanduser("~/.cache/shttst/ultimate_vocal_remover/uvr.zip")


def get_checkpoint():
    if not os.path.exists(CHECKPOINT_CACHE_PATH):
        os.makedirs(os.path.dirname(CHECKPOINT_CACHE_PATH), exist_ok=True)
        resp = requests.get(
            "https://github.com/Anjok07/ultimatevocalremovergui/releases/download/5.0.2/v5_July_2021_5_Models.zip"
        )
        with open(ZIP_PATH, "w+b") as fs:
            fs.write(resp.content)
        with ZipFile(ZIP_PATH, "r") as zipped_vr:
            zipped_vr.extract(
                "models/Vocal_HP_4BAND_3090.pth", os.path.dirname(CHECKPOINT_CACHE_PATH)
            )

        shutil.move(
            os.path.join(
                os.path.dirname(CHECKPOINT_CACHE_PATH), "models/Vocal_HP_4BAND_3090.pth"
            ),
            CHECKPOINT_CACHE_PATH,
        )
        shutil.rmtree(
            os.path.join(os.path.dirname(CHECKPOINT_CACHE_PATH), "models"),
            ignore_errors=False,
            onerror=None,
        )
        os.remove(ZIP_PATH)

    return CHECKPOINT_CACHE_PATH


# Taken from: https://github.com/Anjok07/ultimatevocalremovergui/tree/v5-beta-cml

default_param = {}
default_param["bins"] = 768
default_param["unstable_bins"] = 7  # training only
default_param["reduction_bins"] = 668  # training only
default_param["sr"] = 44100
default_param["pre_filter_start"] = 740
default_param["pre_filter_stop"] = 768
default_param["band"] = {}


default_param["band"][1] = {
    "sr": 11025,
    "hl": 128,
    "n_fft": 1024,
    "crop_start": 0,
    "crop_stop": 186,
    "lpf_start": 37,
    "lpf_stop": 73,
    "res_type": "polyphase",
}

default_param["band"][2] = {
    "sr": 11025,
    "hl": 128,
    "n_fft": 512,
    "crop_start": 4,
    "crop_stop": 185,
    "hpf_start": 36,
    "hpf_stop": 18,
    "lpf_start": 93,
    "lpf_stop": 185,
    "res_type": "polyphase",
}

default_param["band"][3] = {
    "sr": 22050,
    "hl": 256,
    "n_fft": 512,
    "crop_start": 46,
    "crop_stop": 186,
    "hpf_start": 93,
    "hpf_stop": 46,
    "lpf_start": 164,
    "lpf_stop": 186,
    "res_type": "polyphase",
}

default_param["band"][4] = {
    "sr": 44100,
    "hl": 512,
    "n_fft": 768,
    "crop_start": 121,
    "crop_stop": 382,
    "hpf_start": 138,
    "hpf_stop": 123,
    "res_type": "sinc_medium",
}


def int_keys(d):
    r = {}
    for k, v in d:
        if k.isdigit():
            k = int(k)
        r[k] = v
    return r


class ModelParameters(object):
    def __init__(self, config_path=""):
        if ".pth" == pathlib.Path(config_path).suffix:
            import zipfile

            with zipfile.ZipFile(config_path, "r") as zip:
                self.param = json.loads(
                    zip.read("param.json"), object_pairs_hook=int_keys
                )
        elif ".json" == pathlib.Path(config_path).suffix:
            with open(config_path, "r") as f:
                self.param = json.loads(f.read(), object_pairs_hook=int_keys)
        else:
            self.param = default_param

        for k in [
            "mid_side",
            "mid_side_b",
            "mid_side_b2",
            "stereo_w",
            "stereo_n",
            "reverse",
        ]:
            if not k in self.param:
                self.param[k] = False


def crop_center(h1, h2):
    h1_shape = h1.size()
    h2_shape = h2.size()

    if h1_shape[3] == h2_shape[3]:
        return h1
    elif h1_shape[3] < h2_shape[3]:
        raise ValueError("h1_shape[3] must be greater than h2_shape[3]")

    # s_freq = (h2_shape[2] - h1_shape[2]) // 2
    # e_freq = s_freq + h1_shape[2]
    s_time = (h1_shape[3] - h2_shape[3]) // 2
    e_time = s_time + h2_shape[3]
    h1 = h1[:, :, :, s_time:e_time]

    return h1


def wave_to_spectrogram(wave, hop_length, n_fft, mp, multithreading):
    wave_left = np.asfortranarray(wave[0])
    wave_right = np.asfortranarray(wave[1])

    if multithreading:

        def run_thread(**kwargs):
            global spec_left_mt
            spec_left_mt = librosa.stft(**kwargs)

        thread = threading.Thread(
            target=run_thread,
            kwargs={"y": wave_left, "n_fft": n_fft, "hop_length": hop_length},
        )
        thread.start()
        spec_right = librosa.stft(wave_right, n_fft=n_fft, hop_length=hop_length)
        thread.join()
        spec = np.asfortranarray([spec_left_mt, spec_right])
    else:
        spec_left = librosa.stft(wave_left, n_fft=n_fft, hop_length=hop_length)
        spec_right = librosa.stft(wave_right, n_fft=n_fft, hop_length=hop_length)
        spec = np.asfortranarray([spec_left, spec_right])

    return spec


def convert_channels(spec, mp, band):
    cc = mp.param["band"][band].get("convert_channels")

    if mp.param["reverse"]:
        spec_left = np.flip(spec[0])
        spec_right = np.flip(spec[1])
    elif mp.param["mid_side_b"] or "mid_side_b" == cc:
        spec_left = np.add(spec[0], spec[1] * 0.5)
        spec_right = np.subtract(spec[1], spec[0] * 0.5)
    elif mp.param["mid_side_b2"] or "mid_side_b2" == cc:
        spec_left = np.add(spec[1], spec[0] * 0.5)
        spec_right = np.subtract(spec[0], spec[1] * 0.5)
    elif "mid_side_c" == cc:
        spec_left = np.add(spec[0], spec[1] * 0.25)
        spec_right = np.subtract(spec[1], spec[0] * 0.25)
    elif mp.param["mid_side"] or "mid_side" == cc:
        spec_left = np.add(spec[0], spec[1]) / 2
        spec_right = np.subtract(spec[0], spec[1])
    elif mp.param["stereo_n"]:
        spec_left = np.add(spec[0], spec[1] * 0.25) / 0.9375
        spec_right = np.add(spec[1], spec[0] * 0.25) / 0.9375
    else:
        return spec

    return np.asfortranarray([spec_left, spec_right])


def combine_spectrograms(specs, mp):
    l = min([specs[i].shape[2] for i in specs])
    spec_c = np.zeros(shape=(2, mp.param["bins"] + 1, l), dtype=np.complex64)
    offset = 0
    bands_n = len(mp.param["band"])

    for d in range(1, bands_n + 1):
        h = mp.param["band"][d]["crop_stop"] - mp.param["band"][d]["crop_start"]
        s = specs[d][
            :, mp.param["band"][d]["crop_start"] : mp.param["band"][d]["crop_stop"], :l
        ]
        # if 'flip' in mp.param['band'][d]:
        #    s = np.flip(s, 1)
        spec_c[:, offset : offset + h, :l] = s
        offset += h

    if offset > mp.param["bins"]:
        raise ValueError("Too much bins")

    if mp.param["pre_filter_start"] > 0:
        # if bands_n == 1:
        spec_c *= get_lp_filter_mask(
            spec_c.shape[1], mp.param["pre_filter_start"], mp.param["pre_filter_stop"]
        )
        """else:
            gp = 1        
            for b in range(mp.param['pre_filter_start'] + 1, mp.param['pre_filter_stop']):
                g = math.pow(10, -(b - mp.param['pre_filter_start']) * (3.5 - gp) / 20.0)
                gp = g
                spec_c[:, b, :] *= g
        """

    return np.asfortranarray(spec_c)


def spectrogram_to_image(spec, mode="magnitude"):
    if mode == "magnitude":
        if np.iscomplexobj(spec):
            y = np.abs(spec)
        else:
            y = spec
        y = np.log10(y**2 + 1e-8)
    elif mode == "phase":
        if np.iscomplexobj(spec):
            y = np.angle(spec)
        else:
            y = spec

    y -= y.min()
    y *= 255 / y.max()
    img = np.uint8(y)

    if y.ndim == 3:
        img = img.transpose(1, 2, 0)
        img = np.concatenate([np.max(img, axis=2, keepdims=True), img], axis=2)

    return img


def reduce_vocal_aggressively(X, y, softmask):
    v = X - y
    y_mag_tmp = np.abs(y)
    v_mag_tmp = np.abs(v)

    v_mask = v_mag_tmp > y_mag_tmp
    y_mag = np.clip(y_mag_tmp - v_mag_tmp * v_mask * softmask, 0, np.inf)

    return y_mag * np.exp(1.0j * np.angle(y))


def mask_silence(mag, ref, thres=0.2, min_range=64, fade_size=32):
    if min_range < fade_size * 2:
        raise ValueError("min_range must be >= fade_area * 2")

    mag = mag.copy()

    idx = np.where(ref.mean(axis=(0, 1)) < thres)[0]
    starts = np.insert(idx[np.where(np.diff(idx) != 1)[0] + 1], 0, idx[0])
    ends = np.append(idx[np.where(np.diff(idx) != 1)[0]], idx[-1])
    uninformative = np.where(ends - starts > min_range)[0]
    if len(uninformative) > 0:
        starts = starts[uninformative]
        ends = ends[uninformative]
        old_e = None
        for s, e in zip(starts, ends):
            if old_e is not None and s - old_e < fade_size:
                s = old_e - fade_size * 2

            if s != 0:
                weight = np.linspace(0, 1, fade_size)
                mag[:, :, s : s + fade_size] += weight * ref[:, :, s : s + fade_size]
            else:
                s -= fade_size

            if e != mag.shape[2]:
                weight = np.linspace(1, 0, fade_size)
                mag[:, :, e - fade_size : e] += weight * ref[:, :, e - fade_size : e]
            else:
                e += fade_size

            mag[:, :, s + fade_size : e - fade_size] += ref[
                :, :, s + fade_size : e - fade_size
            ]
            old_e = e

    return mag


def trim_specs(a, b):
    l = min([a.shape[2], b.shape[2]])

    return a[:, :, :l], b[:, :, :l]


def cache_or_load(mix_path, inst_path, mp):
    mix_basename = os.path.splitext(os.path.basename(mix_path))[0]
    inst_basename = os.path.splitext(os.path.basename(inst_path))[0]

    # the cache will be common for some model types
    mpp2 = copy.deepcopy(mp.param)
    mpp2.update(
        dict.fromkeys(["mid_side", "mid_side_b", "mid_side_b2", "reverse"], False)
    )

    for d in mpp2["band"]:
        mpp2["band"][d]["convert_channels"] = ""

    cache_dir = "mp{}".format(
        hashlib.sha1(json.dumps(mpp2, sort_keys=True).encode("utf-8")).hexdigest()
    )
    mix_cache_dir = os.path.join("cache", cache_dir)
    inst_cache_dir = os.path.join("cache", cache_dir)

    os.makedirs(mix_cache_dir, exist_ok=True)
    os.makedirs(inst_cache_dir, exist_ok=True)

    mix_cache_path = os.path.join(mix_cache_dir, mix_basename + ".npy")
    inst_cache_path = os.path.join(inst_cache_dir, inst_basename + ".npy")

    if os.path.exists(mix_cache_path) and os.path.exists(inst_cache_path):
        X_spec_m = np.load(mix_cache_path)
        y_spec_m = np.load(inst_cache_path)
    else:
        """
        X_wave, y_wave, X_spec_s, y_spec_s = {}, {}, {}, {}

        for d in range(len(mp.param['band']), 0, -1):
            bp = mp.param['band'][d]

            if d == len(mp.param['band']): # high-end band
                X_wave[d], _ = librosa.load(
                    mix_path, bp['sr'], False, dtype=np.float32, res_type=bp['res_type'])
                y_wave[d], _ = librosa.load(
                    inst_path, bp['sr'], False, dtype=np.float32, res_type=bp['res_type'])
            else: # lower bands
                X_wave[d] = librosa.resample(X_wave[d+1], mp.param['band'][d+1]['sr'], bp['sr'], res_type=bp['res_type'])
                y_wave[d] = librosa.resample(y_wave[d+1], mp.param['band'][d+1]['sr'], bp['sr'], res_type=bp['res_type'])

            X_wave[d], y_wave[d] = align_wave_head_and_tail(X_wave[d], y_wave[d])

            X_spec_s[d] = wave_to_spectrogram(X_wave[d], bp['hl'], bp['n_fft'], mp, False)
            y_spec_s[d] = wave_to_spectrogram(y_wave[d], bp['hl'], bp['n_fft'], mp, False)

        del X_wave, y_wave

        X_spec_m = combine_spectrograms(X_spec_s, mp)
        y_spec_m = combine_spectrograms(y_spec_s, mp)
        """

        X_spec_m = spec_from_file(mix_path, mp)
        y_spec_m = spec_from_file(inst_path, mp)

        X_spec_m, y_spec_m = trim_specs(X_spec_m, y_spec_m)

        if X_spec_m.shape != y_spec_m.shape:
            raise ValueError("The combined spectrograms are different: " + mix_path)

        _, ext = os.path.splitext(mix_path)

        np.save(mix_cache_path, X_spec_m)
        np.save(inst_cache_path, y_spec_m)

    return X_spec_m, y_spec_m


def spectrogram_to_wave(spec, hop_length, mp, band, multithreading):
    import threading

    spec_left = np.asfortranarray(spec[0])
    spec_right = np.asfortranarray(spec[1])
    cc = mp.param["band"][band].get("convert_channels")

    if multithreading:

        def run_thread(**kwargs):
            global wave_left_mt
            wave_left_mt = librosa.istft(**kwargs)

        thread = threading.Thread(
            target=run_thread,
            kwargs={"stft_matrix": spec_left, "hop_length": hop_length},
        )
        thread.start()
        wave_right = librosa.istft(spec_right, hop_length=hop_length)
        thread.join()
        wave_left = wave_left_mt
    else:
        wave_left = librosa.istft(spec_left, hop_length=hop_length)
        wave_right = librosa.istft(spec_right, hop_length=hop_length)

    if mp.param["reverse"]:
        return np.asfortranarray([np.flip(wave_left), np.flip(wave_right)])
    elif mp.param["mid_side_b"] or "mid_side_b" == cc:
        return np.asfortranarray(
            [
                np.subtract(wave_left / 1.25, 0.4 * wave_right),
                np.add(wave_right / 1.25, 0.4 * wave_left),
            ]
        )
    elif mp.param["mid_side_b2"] or "mid_side_b2" == cc:
        return np.asfortranarray(
            [
                np.add(wave_right / 1.25, 0.4 * wave_left),
                np.subtract(wave_left / 1.25, 0.4 * wave_right),
            ]
        )
    elif "mid_side_c" == cc:
        return np.asfortranarray(
            [
                np.subtract(wave_left / 1.0625, wave_right / 4.25),
                np.add(wave_right / 1.0625, wave_left / 4.25),
            ]
        )
    elif mp.param["mid_side"] or "mid_side" == cc:
        return np.asfortranarray(
            [np.add(wave_left, wave_right / 2), np.subtract(wave_left, wave_right / 2)]
        )
    elif mp.param["stereo_n"]:
        return np.asfortranarray(
            [
                np.subtract(wave_left, wave_right * 0.25),
                np.subtract(wave_right, wave_left * 0.25),
            ]
        )
    else:
        return np.asfortranarray([wave_left, wave_right])


def cmb_spectrogram_to_wave(spec_m, mp, extra_bins_h=None, extra_bins=None):
    bands_n = len(mp.param["band"])
    offset = 0

    for d in range(1, bands_n + 1):
        bp = mp.param["band"][d]
        spec_s = np.zeros(
            shape=(2, bp["n_fft"] // 2 + 1, spec_m.shape[2]), dtype=complex
        )
        h = bp["crop_stop"] - bp["crop_start"]
        # if 'flip' in mp.param['band'][d]:
        #    spec_s[:, bp['crop_start']:bp['crop_stop'], :] = np.flip(spec_m[:, offset:offset+h, :], 1)
        # else:
        spec_s[:, bp["crop_start"] : bp["crop_stop"], :] = spec_m[
            :, offset : offset + h, :
        ]

        offset += h
        if d == bands_n:  # high-end
            if extra_bins_h:
                max_bin = bp["n_fft"] // 2
                spec_s[:, max_bin - extra_bins_h : max_bin, :] = extra_bins[
                    :, :extra_bins_h, :
                ]
            if bp["hpf_start"] > 0:
                spec_s *= get_hp_filter_mask(
                    spec_s.shape[1], bp["hpf_start"], bp["hpf_stop"] - 1
                )
            if bands_n == 1:
                wave = spectrogram_to_wave(spec_s, bp["hl"], mp, d, False)
            else:
                wave = np.add(wave, spectrogram_to_wave(spec_s, bp["hl"], mp, d, False))
        else:
            sr = mp.param["band"][d + 1]["sr"]
            if d == 1:  # low-end
                spec_s *= get_lp_filter_mask(
                    spec_s.shape[1], bp["lpf_start"], bp["lpf_stop"]
                )
                wave = librosa.resample(
                    spectrogram_to_wave(spec_s, bp["hl"], mp, d, False),
                    bp["sr"],
                    sr,
                    res_type="sinc_fastest",
                )
            else:  # mid
                spec_s *= get_hp_filter_mask(
                    spec_s.shape[1], bp["hpf_start"], bp["hpf_stop"] - 1
                )
                spec_s *= get_lp_filter_mask(
                    spec_s.shape[1], bp["lpf_start"], bp["lpf_stop"]
                )
                wave2 = np.add(
                    wave, spectrogram_to_wave(spec_s, bp["hl"], mp, d, False)
                )
                wave = librosa.resample(wave2, bp["sr"], sr, res_type="sinc_fastest")

    return wave.T


def cmb_spectrogram_to_wave_ffmpeg(
    spec_m, mp, tmp_basename, extra_bins_h=None, extra_bins=None
):
    import subprocess

    os.makedirs("tmp", exist_ok=True)

    bands_n = len(mp.param["band"])
    offset = 0
    ffmprc = {}

    for d in range(1, bands_n + 1):
        bp = mp.param["band"][d]
        spec_s = np.zeros(
            shape=(2, bp["n_fft"] // 2 + 1, spec_m.shape[2]), dtype=complex
        )
        h = bp["crop_stop"] - bp["crop_start"]
        spec_s[:, bp["crop_start"] : bp["crop_stop"], :] = spec_m[
            :, offset : offset + h, :
        ]
        tmp_wav = os.path.join(
            "tmp", "{}_cstw_b{}_sr{}".format(tmp_basename, d, str(bp["sr"]) + ".wav")
        )
        tmp_wav2 = os.path.join(
            "tmp",
            "{}_cstw_b{}_sr{}".format(tmp_basename, d, str(mp.param["sr"]) + ".wav"),
        )

        offset += h
        if d == bands_n:  # high-end
            if extra_bins_h:
                max_bin = bp["n_fft"] // 2
                spec_s[:, max_bin - extra_bins_h : max_bin, :] = extra_bins[
                    :, :extra_bins_h, :
                ]
            if bp["hpf_start"] > 0:
                spec_s *= get_hp_filter_mask(
                    spec_s.shape[1], bp["hpf_start"], bp["hpf_stop"] - 1
                )
            if bands_n == 1:
                wave = spectrogram_to_wave(spec_s, bp["hl"], mp, d, True)
            else:
                wave = spectrogram_to_wave(spec_s, bp["hl"], mp, d, True)
        else:
            if d == 1:  # low-end
                spec_s *= get_lp_filter_mask(
                    spec_s.shape[1], bp["lpf_start"], bp["lpf_stop"]
                )
            else:  # mid
                spec_s *= get_hp_filter_mask(
                    spec_s.shape[1], bp["hpf_start"], bp["hpf_stop"] - 1
                )
                spec_s *= get_lp_filter_mask(
                    spec_s.shape[1], bp["lpf_start"], bp["lpf_stop"]
                )

            sf.write(
                tmp_wav, spectrogram_to_wave(spec_s, bp["hl"], mp, d, True).T, bp["sr"]
            )
            ffmprc[d] = subprocess.Popen(
                [
                    "ffmpeg",
                    "-hide_banner",
                    "-loglevel",
                    "panic",
                    "-y",
                    "-i",
                    tmp_wav,
                    "-ar",
                    str(mp.param["sr"]),
                    "-ac",
                    "2",
                    "-c:a",
                    "pcm_s16le",
                    tmp_wav2,
                ]
            )

    for s in ffmprc:
        ffmprc[s].communicate()

    for d in range(bands_n - 1, 0, -1):
        os.remove(
            os.path.join(
                "tmp",
                f"{tmp_basename}_cstw_b{d}_sr"
                + str(mp.param["band"][d]["sr"])
                + ".wav",
            )
        )
        tmp_wav2 = os.path.join(
            "tmp", f"{tmp_basename}_cstw_b{d}_sr" + str(mp.param["sr"]) + ".wav"
        )
        wave2, _ = librosa.load(
            tmp_wav2,
            sr=mp.param["sr"],
            mono=False,
            dtype=np.float32,
            res_type="sinc_fastest",
        )
        os.remove(tmp_wav2)
        wave = np.add(wave, wave2)

    return np.float32(wave.T)


"""
def fft_lp_filter(spec, bin_start, bin_stop):
    g = 1.0
    for b in range(bin_start, bin_stop):
        g -= 1 / (bin_stop - bin_start)
        spec[:, b, :] = g * spec[:, b, :]
        
    spec[:, bin_stop:, :] *= 0
    return spec
def fft_hp_filter(spec, bin_start, bin_stop):
    g = 1.0
    for b in range(bin_start, bin_stop, -1):
        g -= 1 / (bin_start - bin_stop)
        spec[:, b, :] = g * spec[:, b, :]
    
    spec[:, 0:bin_stop+1, :] *= 0
    return spec
"""


def get_lp_filter_mask(bins_n, bin_start, bin_stop):
    mask = np.concatenate(
        [
            np.ones((bin_start - 1, 1)),
            np.linspace(1, 0, bin_stop - bin_start + 1)[:, None],
            np.zeros((bins_n - bin_stop, 1)),
        ],
        axis=0,
    )

    return mask


def get_hp_filter_mask(bins_n, bin_start, bin_stop):
    mask = np.concatenate(
        [
            np.zeros((bin_stop + 1, 1)),
            np.linspace(0, 1, 1 + bin_start - bin_stop)[:, None],
            np.ones((bins_n - bin_start - 2, 1)),
        ],
        axis=0,
    )

    return mask


def mirroring(a, spec_m, input_high_end, mp):
    if "mirroring" == a:
        mirror = np.flip(
            np.abs(
                spec_m[
                    :,
                    mp.param["pre_filter_start"]
                    - 10
                    - input_high_end.shape[1] : mp.param["pre_filter_start"]
                    - 10,
                    :,
                ]
            ),
            1,
        )
        mirror = mirror * np.exp(1.0j * np.angle(input_high_end))

        return np.where(
            np.abs(input_high_end) <= np.abs(mirror), input_high_end, mirror
        )

    if "mirroring2" == a:
        mirror = np.flip(
            np.abs(
                spec_m[
                    :,
                    mp.param["pre_filter_start"]
                    - 10
                    - input_high_end.shape[1] : mp.param["pre_filter_start"]
                    - 10,
                    :,
                ]
            ),
            1,
        )
        mi = np.multiply(mirror, input_high_end * 1.7)

        return np.where(np.abs(input_high_end) <= np.abs(mi), input_high_end, mi)


def adjust_aggr(mask, params):
    aggr = params.get("aggr_value", 0.0)

    if aggr != 0:
        if params.get("is_vocal_model"):
            aggr = 1 - aggr

        aggr_l = aggr_r = aggr

        if params["aggr_correction"] is not None:
            aggr_l += params["aggr_correction"]["left"]
            aggr_r += params["aggr_correction"]["right"]

        mask[:, 0, : params["aggr_split_bin"]] = torch.pow(
            mask[:, 0, : params["aggr_split_bin"]], 1 + aggr_l / 3
        )
        mask[:, 0, params["aggr_split_bin"] :] = torch.pow(
            mask[:, 0, params["aggr_split_bin"] :], 1 + aggr_l
        )

        mask[:, 1, : params["aggr_split_bin"]] = torch.pow(
            mask[:, 1, : params["aggr_split_bin"]], 1 + aggr_r / 3
        )
        mask[:, 1, params["aggr_split_bin"] :] = torch.pow(
            mask[:, 1, params["aggr_split_bin"] :], 1 + aggr_r
        )

    return mask


def ensembling(a, specs, sr=44100):
    for i in range(1, len(specs)):
        if i == 1:
            spec = specs[0]

        ln = min([spec.shape[2], specs[i].shape[2]])
        spec = spec[:, :, :ln]
        specs[i] = specs[i][:, :, :ln]
        freq_to_bin = 2 * spec.shape[1] / sr

        if "min_mag" == a:
            spec = np.where(np.abs(specs[i]) <= np.abs(spec), specs[i], spec)
        if "max_mag" == a:
            spec = np.where(np.abs(specs[i]) >= np.abs(spec), specs[i], spec)
        if "mul" == a:
            s1 = specs[i] * spec
            s2 = 0.5 * (specs[i] + spec)
            spec = np.divide(s1, s2, out=np.zeros_like(s1), where=s2 != 0)
        if "crossover" == a:
            bs = int(500 * freq_to_bin)
            be = int(14000 * freq_to_bin)
            spec = specs[i] * get_lp_filter_mask(
                spec.shape[1], bs, be
            ) + spec * get_hp_filter_mask(spec.shape[1], be, bs)
        if "min_mag_co" == a:
            specs[i] += specs[i] * get_hp_filter_mask(
                spec.shape[1], int(14000 * freq_to_bin), int(4000 * freq_to_bin)
            )
            spec = np.where(np.abs(specs[i]) <= np.abs(spec), specs[i], spec)

    return spec


def spec_from_file(filename, mp):
    wave, spec = {}, {}

    for d in range(len(mp.param["band"]), 0, -1):
        bp = mp.param["band"][d]

        if d == len(mp.param["band"]):  # high-end band
            wave, _ = librosa.load(
                filename, bp["sr"], False, dtype=np.float32, res_type=bp["res_type"]
            )

            if len(wave.shape) == 1:  # mono to stereo
                wave = np.array([wave, wave])
        else:  # lower bands
            wave = librosa.resample(
                wave, mp.param["band"][d + 1]["sr"], bp["sr"], res_type=bp["res_type"]
            )

        spec[d] = wave_to_spectrogram(wave, bp["hl"], bp["n_fft"], mp, False)
        spec[d] = convert_channels(spec[d], mp, d)

    return combine_spectrograms(spec, mp)


class Conv2DBNActiv(nn.Module):
    def __init__(self, nin, nout, ksize=3, stride=1, pad=1, dilation=1, activ=nn.ReLU):
        super(Conv2DBNActiv, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(
                nin,
                nout,
                kernel_size=ksize,
                stride=stride,
                padding=pad,
                dilation=dilation,
                bias=False,
            ),
            nn.BatchNorm2d(nout),
            activ(),
        )

    def __call__(self, x):
        return self.conv(x)


class SeperableConv2DBNActiv(nn.Module):
    def __init__(self, nin, nout, ksize=3, stride=1, pad=1, dilation=1, activ=nn.ReLU):
        super(SeperableConv2DBNActiv, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(
                nin,
                nin,
                kernel_size=ksize,
                stride=stride,
                padding=pad,
                dilation=dilation,
                groups=nin,
                bias=False,
            ),
            nn.Conv2d(nin, nout, kernel_size=1, bias=False),
            nn.BatchNorm2d(nout),
            activ(),
        )

    def __call__(self, x):
        return self.conv(x)


class Encoder(nn.Module):
    def __init__(self, nin, nout, ksize=3, stride=1, pad=1, activ=nn.LeakyReLU):
        super(Encoder, self).__init__()
        self.conv1 = Conv2DBNActiv(nin, nout, ksize, 1, pad, activ=activ)
        self.conv2 = Conv2DBNActiv(nout, nout, ksize, stride, pad, activ=activ)

    def __call__(self, x):
        skip = self.conv1(x)
        h = self.conv2(skip)

        return h, skip


class Decoder(nn.Module):
    def __init__(
        self, nin, nout, ksize=3, stride=1, pad=1, activ=nn.ReLU, dropout=False
    ):
        super(Decoder, self).__init__()
        self.conv = Conv2DBNActiv(nin, nout, ksize, 1, pad, activ=activ)
        self.dropout = nn.Dropout2d(0.1) if dropout else None

    def __call__(self, x, skip=None):
        x = F.interpolate(x, scale_factor=2, mode="bilinear", align_corners=True)
        if skip is not None:
            skip = crop_center(skip, x)
            x = torch.cat([x, skip], dim=1)
        h = self.conv(x)

        if self.dropout is not None:
            h = self.dropout(h)

        return h


class ASPPModule(nn.Module):
    def __init__(self, nin, nout, dilations=(4, 8, 16, 32, 64), activ=nn.ReLU):
        super(ASPPModule, self).__init__()
        self.conv1 = nn.Sequential(
            nn.AdaptiveAvgPool2d((1, None)),
            Conv2DBNActiv(nin, nin, 1, 1, 0, activ=activ),
        )
        self.conv2 = Conv2DBNActiv(nin, nin, 1, 1, 0, activ=activ)
        self.conv3 = SeperableConv2DBNActiv(
            nin, nin, 3, 1, dilations[0], dilations[0], activ=activ
        )
        self.conv4 = SeperableConv2DBNActiv(
            nin, nin, 3, 1, dilations[1], dilations[1], activ=activ
        )
        self.conv5 = SeperableConv2DBNActiv(
            nin, nin, 3, 1, dilations[2], dilations[2], activ=activ
        )
        self.bottleneck = nn.Sequential(
            Conv2DBNActiv(nin * 5, nout, 1, 1, 0, activ=activ), nn.Dropout2d(0.1)
        )

    def forward(self, x):
        _, _, h, w = x.size()
        feat1 = F.interpolate(
            self.conv1(x), size=(h, w), mode="bilinear", align_corners=True
        )
        feat2 = self.conv2(x)
        feat3 = self.conv3(x)
        feat4 = self.conv4(x)
        feat5 = self.conv5(x)
        out = torch.cat((feat1, feat2, feat3, feat4, feat5), dim=1)
        bottle = self.bottleneck(out)
        return bottle


class BaseASPPNet(nn.Module):
    def __init__(self, nin, ch, dilations=(4, 8, 16)):
        super(BaseASPPNet, self).__init__()
        self.enc1 = Encoder(nin, ch, 3, 2, 1)
        self.enc2 = Encoder(ch, ch * 2, 3, 2, 1)
        self.enc3 = Encoder(ch * 2, ch * 4, 3, 2, 1)
        self.enc4 = Encoder(ch * 4, ch * 8, 3, 2, 1)

        self.aspp = ASPPModule(ch * 8, ch * 16, dilations)

        self.dec4 = Decoder(ch * (8 + 16), ch * 8, 3, 1, 1)
        self.dec3 = Decoder(ch * (4 + 8), ch * 4, 3, 1, 1)
        self.dec2 = Decoder(ch * (2 + 4), ch * 2, 3, 1, 1)
        self.dec1 = Decoder(ch * (1 + 2), ch, 3, 1, 1)

    def __call__(self, x):
        h, e1 = self.enc1(x)
        h, e2 = self.enc2(h)
        h, e3 = self.enc3(h)
        h, e4 = self.enc4(h)

        h = self.aspp(h)

        h = self.dec4(h, e4)
        h = self.dec3(h, e3)
        h = self.dec2(h, e2)
        h = self.dec1(h, e1)

        return h


class CascadedASPPNet(nn.Module):
    def __init__(self, n_fft):
        super(CascadedASPPNet, self).__init__()
        self.stg1_low_band_net = BaseASPPNet(2, 32)
        self.stg1_high_band_net = BaseASPPNet(2, 32)

        self.stg2_bridge = Conv2DBNActiv(34, 16, 1, 1, 0)
        self.stg2_full_band_net = BaseASPPNet(16, 32)

        self.stg3_bridge = Conv2DBNActiv(66, 32, 1, 1, 0)
        self.stg3_full_band_net = BaseASPPNet(32, 64)

        self.out = nn.Conv2d(64, 2, 1, bias=False)
        self.aux1_out = nn.Conv2d(32, 2, 1, bias=False)
        self.aux2_out = nn.Conv2d(32, 2, 1, bias=False)

        self.max_bin = n_fft // 2
        self.output_bin = n_fft // 2 + 1

        self.offset = 128

    def forward(self, x, params={}):
        mix = x.detach()
        x = x.clone()

        x = x[:, :, : self.max_bin]

        bandw = x.size()[2] // 2
        aux1 = torch.cat(
            [
                self.stg1_low_band_net(x[:, :, :bandw]),
                self.stg1_high_band_net(x[:, :, bandw:]),
            ],
            dim=2,
        )

        h = torch.cat([x, aux1], dim=1)
        aux2 = self.stg2_full_band_net(self.stg2_bridge(h))

        h = torch.cat([x, aux1, aux2], dim=1)
        h = self.stg3_full_band_net(self.stg3_bridge(h))

        mask = torch.sigmoid(self.out(h))
        mask = F.pad(
            input=mask,
            pad=(0, 0, 0, self.output_bin - mask.size()[2]),
            mode="replicate",
        )

        if self.training:
            aux1 = torch.sigmoid(self.aux1_out(aux1))
            aux1 = F.pad(
                input=aux1,
                pad=(0, 0, 0, self.output_bin - aux1.size()[2]),
                mode="replicate",
            )
            aux2 = torch.sigmoid(self.aux2_out(aux2))
            aux2 = F.pad(
                input=aux2,
                pad=(0, 0, 0, self.output_bin - aux2.size()[2]),
                mode="replicate",
            )
            return mask * mix, aux1 * mix, aux2 * mix
        else:
            if params.get("is_vocal_model"):
                return (1.0 - adjust_aggr(mask, params)) * mix

            return adjust_aggr(mask, params) * mix

    def predict(self, x_mag, params={}):
        h = self.forward(x_mag, params)

        if self.offset > 0:
            h = h[:, :, :, self.offset : -self.offset]
            assert h.size()[3] > 0

        return h


def make_padding(width, cropsize, offset):
    left = offset
    roi_size = cropsize - left * 2
    if roi_size == 0:
        roi_size = cropsize
    right = roi_size - (width % roi_size) + left

    return left, right, roi_size


class VocalRemover(object):
    def __init__(self, model, device, window_size=512):
        self.model = model
        self.offset = model.offset
        self.device = device
        self.window_size = window_size

    def _execute(self, X_mag_pad, roi_size, n_window, params):
        self.model.eval()
        with torch.no_grad():
            preds = []
            for i in range(n_window):
                start = i * roi_size
                X_mag_window = X_mag_pad[None, :, :, start : start + self.window_size]
                X_mag_window = torch.from_numpy(X_mag_window).to(self.device)

                pred = self.model.predict(X_mag_window, params)

                pred = pred.detach().cpu().numpy()
                preds.append(pred[0])

            pred = np.concatenate(preds, axis=2)

        return pred

    def preprocess(self, X_spec):
        X_mag = np.abs(X_spec)
        X_phase = np.angle(X_spec)

        return X_mag, X_phase

    def inference(self, X_spec, params):
        X_mag, X_phase = self.preprocess(X_spec)

        coef = X_mag.max()
        X_mag_pre = X_mag / coef

        n_frame = X_mag_pre.shape[2]
        pad_l, pad_r, roi_size = make_padding(n_frame, self.window_size, self.offset)
        n_window = int(np.ceil(n_frame / roi_size))

        X_mag_pad = np.pad(X_mag_pre, ((0, 0), (0, 0), (pad_l, pad_r)), mode="constant")

        pred = self._execute(X_mag_pad, roi_size, n_window, params)
        pred = pred[:, :, :n_frame]

        return pred * coef, X_mag, np.exp(1.0j * X_phase)

    def inference_tta(self, X_spec, params):
        X_mag, X_phase = self.preprocess(X_spec)

        coef = X_mag.max()
        X_mag_pre = X_mag / coef

        n_frame = X_mag_pre.shape[2]
        pad_l, pad_r, roi_size = make_padding(n_frame, self.window_size, self.offset)
        n_window = int(np.ceil(n_frame / roi_size))

        X_mag_pad = np.pad(X_mag_pre, ((0, 0), (0, 0), (pad_l, pad_r)), mode="constant")

        pred = self._execute(X_mag_pad, roi_size, n_window, params)
        pred = pred[:, :, :n_frame]

        pad_l += roi_size // 2
        pad_r += roi_size // 2
        n_window += 1

        X_mag_pad = np.pad(X_mag_pre, ((0, 0), (0, 0), (pad_l, pad_r)), mode="constant")

        pred_tta = self._execute(X_mag_pad, roi_size, n_window, params)
        pred_tta = pred_tta[:, :, roi_size // 2 :]
        pred_tta = pred_tta[:, :, :n_frame]

        return (pred + pred_tta) * 0.5 * coef, X_mag, np.exp(1.0j * X_phase)


class ShmartUltimateVocalRemover:
    def __init__(self) -> None:
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.mp = ModelParameters()
        model = CascadedASPPNet(self.mp.param["bins"] * 2)

        model.load_state_dict(torch.load(get_checkpoint(), map_location="cpu"))
        model.to(self.device)

        self.model = model
        self.vr = VocalRemover(self.model, self.device)

    def __call__(
        self,
        wav_path,
        tta=False,
        high_end_process="mirroring",
        aggressiveness=0.6,
        is_vocal_model=True,
        sr=22050,
    ):
        # adapted from https://github.com/Anjok07/ultimatevocalremovergui/blob/v5-beta-cml/inference.py
        mp = self.mp
        bands_n = len(mp.param["band"])
        bp = mp.param["band"][bands_n]
        input_is_mono = False

        X_spec = {}
        X, sr = librosa.load(
            wav_path, sr=sr, mono=False, dtype=np.float32, res_type=bp["res_type"]
        )

        if X.ndim == 1:
            input_is_mono = True
            X = np.asarray([X, X])

        X_spec[bands_n] = wave_to_spectrogram(X, bp["hl"], bp["n_fft"], mp, True)
        X_spec[bands_n] = convert_channels(X_spec[bands_n], mp, bands_n)

        if np.max(X[0]) == 0.0:
            print("Empty audio file!")
            raise ValueError("Empty audio file")

        if high_end_process != "none":
            input_high_end_h = (bp["n_fft"] // 2 - bp["crop_stop"]) + (
                mp.param["pre_filter_stop"] - mp.param["pre_filter_start"]
            )
            input_high_end = X_spec[bands_n][
                :, bp["n_fft"] // 2 - input_high_end_h : bp["n_fft"] // 2, :
            ]

        for d in range(bands_n - 1, 0, -1):
            bp = mp.param["band"][d]

            X = librosa.resample(
                X,
                orig_sr=mp.param["band"][d + 1]["sr"],
                target_sr=bp["sr"],
                res_type=bp["res_type"],
            )
            X_spec[d] = wave_to_spectrogram(X, bp["hl"], bp["n_fft"], mp, True)
            X_spec[d] = convert_channels(X_spec[d], mp, d)

        X_spec = combine_spectrograms(X_spec, mp)

        pd = {
            "aggr_value": aggressiveness,
            "aggr_split_bin": mp.param["band"][1]["crop_stop"],
            "aggr_correction": mp.param.get("aggr_correction"),
            "is_vocal_model": is_vocal_model,
        }

        if tta:
            pred, X_mag, X_phase = self.vr.inference_tta(X_spec, pd)
        else:
            pred, X_mag, X_phase = self.vr.inference(X_spec, pd)

        ffmpeg_tmp_filename = "inst_tmp"
        y_spec_m = pred * X_phase

        if high_end_process == "bypass":
            instruments_wave = cmb_spectrogram_to_wave_ffmpeg(
                y_spec_m, mp, ffmpeg_tmp_filename, input_high_end_h, input_high_end
            )
        elif high_end_process.startswith("mirroring"):
            input_high_end_ = mirroring(high_end_process, y_spec_m, input_high_end, mp)
            instruments_wave = cmb_spectrogram_to_wave_ffmpeg(
                y_spec_m, mp, ffmpeg_tmp_filename, input_high_end_h, input_high_end_
            )
        else:
            instruments_wave = cmb_spectrogram_to_wave_ffmpeg(
                y_spec_m, mp, ffmpeg_tmp_filename
            )

        if input_is_mono:
            instruments_wave = instruments_wave.mean(axis=1, keepdims=True)

        instruments_wave = torch.from_numpy(instruments_wave).permute(1, 0)

        ffmpeg_tmp_filename = "vocal_tmp"
        v_spec_m = X_spec - y_spec_m

        if high_end_process.startswith("mirroring"):
            input_high_end_ = mirroring(high_end_process, v_spec_m, input_high_end, mp)
            vocals_wave = cmb_spectrogram_to_wave_ffmpeg(
                v_spec_m, mp, ffmpeg_tmp_filename, input_high_end_h, input_high_end_
            )
        else:
            vocals_wave = cmb_spectrogram_to_wave_ffmpeg(
                v_spec_m, mp, ffmpeg_tmp_filename
            )

        if input_is_mono:
            vocals_wave = vocals_wave.mean(axis=1, keepdims=True)

        vocals_wave = torch.from_numpy(vocals_wave).permute(1, 0)

        return convert_to_mono_channel(vocals_wave), convert_to_mono_channel(
            instruments_wave
        )


if __name__ == "__main__":
    vocals, instruments = ShmartUltimateVocalRemover()(
        "/debug/org.wav", tta=True, is_vocal_model=True, aggressiveness=0.01
    )
    os.makedirs("/content/vr", exist_ok=True)
    save_audio("/content/vr/vocals.wav", vocals)
    save_audio("/content/vr/instruments.wav", instruments)
