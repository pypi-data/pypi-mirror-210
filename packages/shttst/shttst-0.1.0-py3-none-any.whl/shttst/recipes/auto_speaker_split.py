import numpy as np
import os
import shutil
from shttst.files import append_file, get_audio_files, read_lines
from shttst.audio.tools import get_custom_embedding
from shttst.models import ShmartSpeakerClustering
from tqdm import tqdm


def divide_into_dirs(predicted_path, dest_path, move=False):
    to_process = [x.split("|") for x in read_lines(predicted_path)]
    for file, label in tqdm(to_process):
        dest_dir = os.path.join(dest_path, label, "wavs")
        os.makedirs(dest_dir, exist_ok=True)
        dest = os.path.join(dest_dir, os.path.basename(file))
        if move:
            shutil.move(file, dest)
        else:
            shutil.copy(file, dest)


def read_embeddings(embeddings_path: str):
    def np_string2array(string):
        return [
            float(x)
            for x in [
                x for x in string.replace("]", "").replace("[", "").split(" ") if len(x)
            ]
        ]

    lines = read_lines(embeddings_path)
    return {f: np_string2array(e) for (f, e) in [l.split("|") for l in lines]}


def auto_speaker_split(root_path: str, method="titanet"):
    ssc = ShmartSpeakerClustering(method=method)
    embedding_path = os.path.join(root_path, f"{method}.csv")
    emb_dict = {}
    if os.path.exists(embedding_path):
        emb_dict = read_embeddings(embedding_path)
    audio_files = get_audio_files(root_path)

    for file in tqdm(audio_files):
        if file not in emb_dict:
            emb_dict[file] = get_custom_embedding(file, method).numpy()
            append_file(embedding_path, f"{file}|{np.array2string(emb_dict[file])}\n")

    clustering = ssc.predict(list(emb_dict.values()))

    predicted_path = os.path.join(root_path, "predicted.csv")
    if os.path.exists(predicted_path):
        os.remove(predicted_path)

    for i, file in enumerate(tqdm(emb_dict.keys())):
        label = str(clustering.labels_[i])
        append_file(predicted_path, f"{file}|{label}\n")


if __name__ == "__main__":
    # auto_speaker_split("/outdir/g3")
    divide_into_dirs("/outdir/g3/predicted.csv", "/outdir/splitted")
