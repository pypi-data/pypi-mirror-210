import os
from dataclasses import dataclass


@dataclass
class ShmartTranscriptionLine:
    name: str
    text: str
    speaker: str = ""
    category: str = ""
    duration: float = -1

    def serialize(self) -> str:
        return f"{'|'.join([self.name, self.text, self.speaker, self.category, str(self.duration)])}\n"

    def get_audio_path(self, wavs_dir_path: str) -> str:
        return os.path.join(wavs_dir_path, f"{self.name}.wav")
