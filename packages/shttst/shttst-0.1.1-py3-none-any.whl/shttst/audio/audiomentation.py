import torch
from audiomentations import AddShortNoises, PolarityInversion, AddBackgroundNoise, TanhDistortion, AddGaussianNoise, AddGaussianSNR
from random import shuffle, random

from shttst.audio.utils import load_audio, save_audio

def get_noise_transform(noise_dir="/content/MUSAN"):
    transforms = [AddShortNoises(
        sounds_path=noise_dir,
        min_snr_in_db=15.0,
        max_snr_in_db=25.0,
        noise_rms="relative_to_whole_input",
        min_time_between_sounds=2.0,
        max_time_between_sounds=8.0,
        noise_transform=PolarityInversion(),
        p=1.0
    ), AddBackgroundNoise(
        sounds_path=noise_dir,
        min_snr_in_db=15.0,
        max_snr_in_db=25.0,
        noise_transform=PolarityInversion(),
        p=1.0
    ), TanhDistortion(
        min_distortion=0.45,
        max_distortion=0.85,
        p=1.0
    ), AddGaussianNoise(
        min_amplitude=0.001,
        max_amplitude=0.015,
        p=1.0
    ), AddGaussianSNR(
        min_snr_in_db=15.0,
        max_snr_in_db=35.0,
        p=1.0
    )]
    shuffle(transforms)
    return transforms[0]

def apply_random_noise(audio_tensor, sr=22050, noise_dir="/content/MUSAN"):
    return torch.FloatTensor(get_noise_transform(noise_dir)(audio_tensor[0].numpy(), sr)).unsqueeze(0)

if __name__ == '__main__':
    wave, sr = load_audio('/content/manual/Bezi/wavs/DIA_BaalIsidro_GimmeKraut_15_00.wav')
    save_audio('/content/noise.wav', apply_random_noise(wave, sr))