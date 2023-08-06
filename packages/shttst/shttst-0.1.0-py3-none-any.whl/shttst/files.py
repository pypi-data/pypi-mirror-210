import os
import shutil
from typing import List
from pathlib import Path

def get_files(dir_path: str, extensions = ['*'], name='*') -> List[str]:
    paths = []
    for ext in extensions:
        paths.extend([str(f) for f in Path(dir_path).rglob(f'{name}.{ext}')])
    return paths

def get_audio_files(dir_path: str) -> List[str]:
    return get_files(dir_path, ['wav', 'ogg', 'flac', 'mp3'])

def read_lines(text_file_path: str) -> List[str]:
    with open(text_file_path, 'r', encoding='utf-8') as fs:
        return [f.rstrip().replace('\n', '') for f in fs.readlines()]

def write_file(text_file_path: str, content: str, mode='w') -> None:
    with open(text_file_path, mode, encoding='utf-8') as fs:
        fs.write(content)

def append_file(text_file_path: str, content: str) -> None:
    write_file(text_file_path, content, 'a')

def get_parent_dir(file_path: str) -> str:
    return os.path.normpath(os.path.join(os.path.dirname(file_path), os.path.pardir))

def move_to_parent(file_path: str):
    if os.path.exists(file_path):
        shutil.move(file_path, os.path.join(get_parent_dir(file_path), os.path.basename(file_path)))

def replace_ext(file_path: str, ext: str):
    assert ext.startswith('.')
    return f"{Path(file_path).stem}{ext}"

def destroy_file(file_path: str) -> None:
    with open(file_path, 'w') as fs:
        fs.close()
    os.remove(file_path)

if __name__ == '__main__':
    # print(get_audio_files('/content/yt')[:5])
    print(read_lines('/content/yt/test.txt')[:5])
