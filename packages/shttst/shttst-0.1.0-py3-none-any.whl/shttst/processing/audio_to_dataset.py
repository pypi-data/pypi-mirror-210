import os
import shutil

from shttst.audio import classify_audio_file, clean_audio_noise, split_by_vad
from shttst.files import destroy_file, get_parent_dir
from shttst.recipes.transcribe_directory import transcribe_directory

class AudioToDatasetProcessor():
    def __init__(self, keep_not_fine=False, denoise_all=False, use_classifier=True):
        self.keep_not_fine = keep_not_fine
        self.denoise_all = denoise_all
        self.use_classifier = use_classifier

    def __call__(self, file_path, vad_max_duration=14, vad_min_silence=500):
        # 1. Split
        vad_files = split_by_vad(file_path, vad_max_duration, vad_min_silence)
        print(f'splitted into {len(vad_files)} audio files.')
        destroy_file(file_path)

        #2. Denoise + Classify
        self._clean_audio_files(vad_files)
        
        if self.use_classifier:
            fine_files = self._clasify_files(vad_files)
            print(f'Got {len(fine_files)} fine audio files.')

        #3. Transcribe
        transcribe_directory(get_parent_dir(file_path), classify=False, remove_bad=not self.keep_not_fine)
    
    def _clean_audio_files(self, audio_files):
        if not self.denoise_all:
            return
        
        for file in audio_files:
            clean_audio_noise(file)

    
    def _clasify_files(self, audio_files):
        fine_files = []
        for file in audio_files:
            label = classify_audio_file(file)
            if label != 'fine':
                if not self.denoise_all:
                    clean_audio_noise(file)
                    label = classify_audio_file(file)
            
            if label != 'fine':
                if self.keep_not_fine:
                    trash_dir = os.path.join(get_parent_dir(file), 'trashed', label)
                    os.makedirs(trash_dir, exist_ok=True)
                    shutil.move(file, os.path.join(trash_dir, os.path.basename(file)))
                else:
                    destroy_file(file)
            else:
                fine_files.append(file)
        return fine_files