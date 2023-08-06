import os
from random import shuffle
from shttst.dataset import scan_dir
from shttst.dataset.transcriptions import read_transcriptions_file, write_transcriptions

def prepare_traininig_sets(root_dir: str, test_percent=2):
    metadata_files = scan_dir(root_dir)
    combined_train = []
    combined_test = []
    for meta_path in metadata_files:
        speaker_dir = os.path.relpath(os.path.dirname(meta_path), root_dir)
        transcriptions = read_transcriptions_file(meta_path)
        
        for transcription in transcriptions:
            transcription.name = os.path.join(speaker_dir, 'wavs', f"{transcription.name}.wav")
        
        shuffle(transcriptions)
    
        split_point = int(len(transcriptions) * test_percent / 100)
        combined_test.extend(transcriptions[:split_point])
        combined_train.extend(transcriptions[split_point:])
    
    write_transcriptions(os.path.join(root_dir, 'train.txt'), combined_train)
    write_transcriptions(os.path.join(root_dir, 'test.txt'), combined_test)

if __name__ == '__main__':
    prepare_traininig_sets('/content/todo/rmf')