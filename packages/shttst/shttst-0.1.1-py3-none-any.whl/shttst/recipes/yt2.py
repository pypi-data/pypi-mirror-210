import os
from shttst.recipes.advanced_split import advanced_audio_split
from shttst.recipes.auto_speaker_split import auto_speaker_split, divide_into_dirs
from shttst.recipes.transcribe_directory import transcribe_directory
from yt_dlp import YoutubeDL
from yt_dlp.postprocessor import PostProcessor

from shttst.processing import AudioToDatasetProcessor


class ShmartYTDPostProcessor(PostProcessor):
    def __init__(
        self,
        vad_max_duration=14,
        vad_min_silence=150,
        downloader=None,
    ):
        super().__init__(downloader)
        self.vad_max_duration = vad_max_duration
        self.vad_min_silence = vad_min_silence

    def run(self, info):
        advanced_audio_split(
            info["filepath"],
            desired_max_speech_duration=self.vad_max_duration,
            min_silence_duration=self.vad_min_silence,
        )

        return [], info


def create_dataset_from_yt_playlist(
    playlist_id,
    output_dir="\\content\\yt_dlp",
    playlist_start=0,
    playlist_end=None,
    vad_max_duration=14,
    vad_min_silence=200,
):
    ydl_opts = {
        "format": "m4a/bestaudio/best",
        "postprocessors": [
            {  # Extract audio using ffmpeg
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
            }
        ],
        "playliststart": playlist_start,
        "playlistend": playlist_end,
        # "outtmpl": os.path.join(output_dir, "%(id)s", "wavs", "%(id)s"),
        "outtmpl": os.path.join(output_dir, "%(id)s"),
        "quiet": True,
    }

    with YoutubeDL(ydl_opts) as ytd:
        ytd.add_post_processor(
            ShmartYTDPostProcessor(
                vad_max_duration,
                vad_min_silence,
            ),
            when="post_process",
        )
        ytd.download(playlist_id)

        auto_speaker_split(output_dir)
        divide_into_dirs(
            os.path.join(output_dir, "predicted.csv"), output_dir, move=True
        )
        transcribe_directory(output_dir, classify=False)


if __name__ == "__main__":
    create_dataset_from_yt_playlist(
        "https://www.youtube.com/watch?v=PpV_T_Fswfo&list=PLvwAEEkypa6BRMRFIcnJGBtlP1L0gHhUF",
        output_dir="c:\\content\\swl",
        vad_max_duration=14,
        vad_min_silence=200,
        playlist_start=0,
    )
