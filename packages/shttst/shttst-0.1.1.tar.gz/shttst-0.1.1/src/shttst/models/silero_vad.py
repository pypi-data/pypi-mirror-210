import os
import torch

from shttst.audio.utils import make_default_tts_wav, resample, save_audio
from shttst.files import destroy_file


class ShmartSileroVad:
    def __init__(self) -> None:
        vad_model, utils = torch.hub.load(
            repo_or_dir="snakers4/silero-vad",
            model="silero_vad",
            force_reload=False,
            onnx=False,
        )
        self.vad_model = vad_model
        self.get_speech_timestamps = utils[0]
        # self.read_audio = utils[2] # replaced with resample to sr=16000 as silero used faulty torchaudio method (see: resample from shttst.audio.utils)

    def vad_process(
        self,
        audio_file,
        min_silence_duration=200,
        initial_max_speech_duration=30,
        desired_max_speech_duration=14,
    ):
        with torch.no_grad():
            tts_sr = 22050
            silero_sr = 16000
            end_frames_fix = int(tts_sr / 12)
            frames_scale = tts_sr / silero_sr

            audio_to_split = make_default_tts_wav(audio_file)

            timestamps = self.get_speech_timestamps(
                resample(audio_to_split, tts_sr, silero_sr),
                self.vad_model,
                0.90,  # speech prob threshold
                16000,  # sample rate
                800,  # min speech duration in ms
                initial_max_speech_duration,  # max speech duration in seconds
                min_silence_duration,  # min silence duration
                512,  # window size
                200,  # spech pad ms
            )

            timestamps = self._merge_timestamps(
                timestamps, silero_sr * desired_max_speech_duration
            )

            result = []

            for i, t in enumerate(timestamps):
                start = int(t["start"] * frames_scale)
                end = int(t["end"] * frames_scale) + end_frames_fix
                result_audio = audio_to_split[..., start:end]
                if result_audio.size(0) > 0:
                    name = os.path.splitext(os.path.basename(audio_file))[0]
                    sample_path = os.path.join(
                        os.path.dirname(audio_file), f"{name}_{i}.wav"
                    )
                    save_audio(sample_path, result_audio)
                    if result_audio.size(1) > tts_sr * desired_max_speech_duration:
                        result.extend(
                            self.vad_process(
                                sample_path,
                                min_silence_duration * 0.75,
                                desired_max_speech_duration * 0.75,
                            )
                        )
                        destroy_file(sample_path)
                    else:
                        result.append(sample_path)

            return result

    def _merge_timestamps(self, timestamps, max_frames):
        result = []
        current = None
        for i, t in enumerate(timestamps):
            if not current:
                current = t
                continue
            if t["end"] - current["start"] > max_frames:
                result.append(current)
                current = t
                continue
            else:
                current["end"] = t["end"]

        return result
