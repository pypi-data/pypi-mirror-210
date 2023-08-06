from dataclasses import dataclass
import os
import shutil
from typing import List
from shttst.dataset.transcription_line import ShmartTranscriptionLine
from shttst.files import destroy_file, get_files
from shttst.dataset.transcriptions import read_transcriptions_file, write_transcriptions


@dataclass
class ShmartDatasetDirectory:
    path: str
    transcriptions: List[ShmartTranscriptionLine]

    @property
    def metadata_path(self):
        return os.path.join(self.path, "metadata.csv")

    @property
    def wavs_path(self):
        return os.path.join(self.path, "wavs")


def scan_dir(dir_path: str):
    dataset_dirs = get_files(dir_path, ["csv"], "metadata")
    return [
        ShmartDatasetDirectory(
            os.path.dirname(meta_path), read_transcriptions_file(meta_path)
        )
        for meta_path in dataset_dirs
    ]


def check_dataset(dataset: ShmartDatasetDirectory, delete_missing=False):
    wavs_dir_path = os.path.join(dataset.path, "wavs")
    transcriptions = dataset.transcriptions
    transcribed_files = [x.get_audio_path(wavs_dir_path) for x in transcriptions]
    if not os.path.exists(wavs_dir_path):
        raise Exception(f"{wavs_dir_path} does not exist, check dataset structure.")
    wavs = get_files(wavs_dir_path, ["wav"])
    transcribed_wavs = [x for x in wavs if x in transcribed_files]
    missing_wavs = [x for x in transcribed_files if x not in wavs]
    missing_transcriptions = [x for x in wavs if x not in transcribed_files]
    if delete_missing:
        if len(missing_wavs):
            transcriptions = [
                x
                for x in transcriptions
                if x.get_audio_path(wavs_dir_path) not in missing_wavs
            ]
            shutil.move(dataset.metadata_path, f"{dataset.metadata_path}.bak")
            write_transcriptions(dataset.metadata_path, transcriptions)
        for missing_transcription in missing_transcriptions:
            destroy_file(missing_transcription)
    return transcriptions, transcribed_wavs, missing_wavs, missing_transcriptions


if __name__ == "__main__":
    dir_path = "/content/manual"
    for dataset in scan_dir(dir_path):
        try:
            print(dataset.transcriptions[0].get_audio_path(dataset.wavs_path))
        except Exception as e:
            print(e)
