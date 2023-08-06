import os
from pathlib import Path
from shttst.audio import make_default_tts_wav, save_audio
from shttst.files import get_audio_files, replace_ext
from tqdm import tqdm

def prepare_tts_wavs(dir_to_lookup: str, destination_dir: str):
    audio_list = get_audio_files(dir_to_lookup)
    
    for file_path in tqdm(audio_list):
        try:
            audio = make_default_tts_wav(file_path)
            relative_dir = str(Path(os.path.relpath(file_path, dir_to_lookup)).parent)
            file_name = f"{replace_ext(file_path)}.wav"
            file_dir = os.path.join(destination_dir, relative_dir)
            os.makedirs(file_dir, exist_ok=True)
            save_audio(os.path.join(file_dir, file_name), audio)
        except Exception as e:
            print(file_path)
            print(e)

if __name__ == '__main__':
    prepare_tts_wavs('D:/audio datasety/gry/skyrim/test', '/content/skyrim')