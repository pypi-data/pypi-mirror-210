import os
import torch

from shttst.audio.utils import make_default_tts_wav, resample, save_audio
from shttst.files import destroy_file
from shttst.audio.tools import get_model

from pyannote.audio import Pipeline

diarization_model_pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization")


def advanced_audio_split(
    audio_path,
    min_silence_duration=150,
    desired_max_speech_duration=14,
    min_sample_length=2.2,
):
    tts_sr = 22050
    silero_sr = 16000
    vad_model, utils = torch.hub.load(
        repo_or_dir="snakers4/silero-vad",
        model="silero_vad",
        force_reload=False,
        onnx=False,
    )

    get_speech_timestamps = utils[0]

    from nemo.collections.asr.models import EncDecSpeakerLabelModel

    titanet_model: EncDecSpeakerLabelModel = get_model("titanet")

    def _verify_samples_speaker(audio, t1, t2):
        a1 = audio[..., t1["start"] : t1["end"]]
        a2 = audio[..., t2["start"] : t2["end"]]
        a1_path, a2_path = "tmp1.wav", "tmp2.wav"
        save_audio(a1_path, a1, target_sr=silero_sr)
        save_audio(a2_path, a2, target_sr=silero_sr)

        is_same_speaker = titanet_model.verify_speakers(a1_path, a2_path)
        os.remove(a1_path)
        os.remove(a2_path)
        return is_same_speaker

    def _is_single_speaker(audio_path):
        diarization = diarization_model_pipeline(audio_path)
        speakers = set(
            [speaker for _, _, speaker in diarization.itertracks(yield_label=True)]
        )
        return len(speakers) == 1

    def _merge_timestamps(timestamps, max_frames, audio):
        merge_result = []
        current = None
        for t in timestamps:
            if not current:
                current = t
                continue
            if t["end"] - current["start"] > max_frames or not _verify_samples_speaker(
                audio, current, t
            ):
                merge_result.append(current)
                current = t
                continue
            else:
                current["end"] = t["end"]

        return merge_result

    def process_vad(
        audio_path, min_silence_duration=150, desired_max_speech_duration=14
    ):
        with torch.no_grad():
            end_frames_fix = 1200
            frames_scale = tts_sr / silero_sr

            audio_to_split = make_default_tts_wav(audio_path)
            resampled = resample(audio_to_split, tts_sr, silero_sr)

            timestamps = get_speech_timestamps(
                resampled,
                vad_model,
                0.95,  # speech prob threshold
                16000,  # sample rate
                min_sample_length * 400,  # min speech duration in ms
                26,  # max speech duration in seconds
                min_silence_duration,  # min silence duration
                512,  # window size
                150,  # speech pad ms
            )

            timestamps = _merge_timestamps(
                timestamps, silero_sr * desired_max_speech_duration, resampled
            )

            result = []

            for i, t in enumerate(timestamps):
                start = int(t["start"] * frames_scale)
                end = int(t["end"] * frames_scale) + end_frames_fix
                if end - start > tts_sr * min_sample_length:
                    result_audio = audio_to_split[..., start:end]
                    name = os.path.splitext(os.path.basename(audio_path))[0]
                    sample_path = os.path.join(
                        os.path.dirname(audio_path), f"{name}_{i}.wav"
                    )
                    save_audio(sample_path, result_audio)
                    if result_audio.size(1) > tts_sr * desired_max_speech_duration:
                        result.extend(
                            process_vad(
                                sample_path,
                                min_silence_duration * 0.75,
                                desired_max_speech_duration * 0.75,
                            )
                        )
                        destroy_file(sample_path)
                    else:
                        if _is_single_speaker(sample_path):
                            result.append(sample_path)
                        else:
                            destroy_file(sample_path)

            return result

    process_vad(audio_path, min_silence_duration, desired_max_speech_duration)
    os.remove(audio_path)
