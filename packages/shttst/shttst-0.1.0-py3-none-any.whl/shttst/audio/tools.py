import huggingface_hub
import torch
from typing import Tuple

from audclas.tortoise_audio_classifier import TortoiseAudioClassifier
from shttst.audio.utils import save_audio

initialized_models = {}


def initialize_model(type):
    model = None

    if type == "classifier":
        model = TortoiseAudioClassifier()
    elif type == "denoiser":
        from shttst.models import ShmartUltimateVocalRemover

        model = ShmartUltimateVocalRemover()
    elif type == "titanet":
        from nemo.collections.asr.models import EncDecSpeakerLabelModel

        model = EncDecSpeakerLabelModel.from_pretrained(
            "nvidia/speakerverification_en_titanet_large", map_location="cpu"
        )
        model.cuda().eval()
    elif type == "resemblyzer":
        from resemblyzer import VoiceEncoder

        model = VoiceEncoder("cuda", verbose=False)
        model.eval()
    elif type == "vad":
        from shttst.models import ShmartSileroVad

        model = ShmartSileroVad()
    elif type == "whisper":
        from faster_whisper import WhisperModel

        model_path = huggingface_hub.snapshot_download("shmart/shmisper-medium-PL")
        model = WhisperModel(model_path, device="cuda", compute_type="float16")

    initialized_models[type] = model


def get_model(type):
    if type not in initialized_models:
        initialize_model(type)

    return initialized_models[type]


def classify_audio_file(file_path: str) -> str:
    model: TortoiseAudioClassifier = get_model("classifier")
    return model(file_path)


def split_by_vad(file_path: str, max_duration: int, min_silence: int) -> str:
    from shttst.models import ShmartSileroVad

    model: ShmartSileroVad = get_model("vad")
    return model.vad_process(
        file_path,
        min_silence_duration=min_silence,
        desired_max_speech_duration=max_duration,
    )


def clean_audio_noise(file_path: str) -> str:
    from shttst.models import ShmartUltimateVocalRemover

    vr_model: ShmartUltimateVocalRemover = get_model("denoiser")
    vocals, instruments = vr_model(file_path, tta=True)
    save_audio(file_path, vocals)


def get_custom_embedding(file_path, type="titanet"):
    if type == "titanet":
        from nemo.collections.asr.models import EncDecSpeakerLabelModel

        titanet_model: EncDecSpeakerLabelModel = get_model(type)
        return titanet_model.get_embedding(file_path).squeeze(0).cpu()
    elif type == "resemblyzer":
        from resemblyzer import VoiceEncoder, preprocess_wav

        wav = preprocess_wav(file_path)
        resemblyzer_model: VoiceEncoder = get_model(type)
        return torch.from_numpy(resemblyzer_model.embed_utterance(wav))


def get_transcription(
    audio_path,
    options={
        "language": "pl",
        "beam_size": 5,
        "without_timestamps": True,
        "suppress_tokens": [],
        "log_prob_threshold": None,
        "no_speech_threshold": 0.06,
    },
) -> Tuple[str, float]:
    from faster_whisper import WhisperModel

    model: WhisperModel = get_model("whisper")
    result, info = model.transcribe(audio_path, **options)
    try:
        return " ".join([r.text for r in result]), info.duration
    except:
        return "", -1


def denoise_cli(args):
    if args:
        print(args)
    else:
        import sys

        print(sys.argv)


if __name__ == "__main__":
    # get_custom_embedding('\\content\\cyber\\2077\\wavs\\55.wav')
    clean_audio_noise("/users/user/downloads/orgina.wav")
