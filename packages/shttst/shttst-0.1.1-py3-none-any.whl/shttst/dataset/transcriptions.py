from typing import List

from shttst.files import read_lines, write_file
from shttst.dataset import ShmartTranscriptionLine


def read_transcriptions_file(file_path):
    return [
        ShmartTranscriptionLine(a,b,c,d,float(e))
        for a,b,c,d,e in [line.split('|') for line in  read_lines(file_path)]
    ]

def write_transcriptions(file_path, transcriptions: List[ShmartTranscriptionLine]) -> None:
    content = '\n'.join([f"{x.name}|{x.text}|{x.speaker}|{x.category}|{x.duration}" for x in transcriptions])
    write_file(file_path, content)

if __name__ == '__main__':
    write_transcriptions('test.txt', read_transcriptions_file('/content/yt/test.txt')[:5])