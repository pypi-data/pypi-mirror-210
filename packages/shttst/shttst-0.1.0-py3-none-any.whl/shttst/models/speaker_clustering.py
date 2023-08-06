import numpy as np

np.set_printoptions(linewidth=np.inf)
import os

from sklearn.cluster import AgglomerativeClustering
from shttst.dataset.dataset_files import scan_dir
from shttst.files import append_file, read_lines
from shttst.audio.tools import get_custom_embedding
from tqdm import tqdm


class ShmartSpeakerClustering:
    def __init__(self, distance_threshold=None, method="titanet") -> None:
        self.distance_threshold = distance_threshold
        self.method = method

    def predict(self, embeddings):
        distance_threshold = (
            self.distance_threshold
            if self.distance_threshold
            else self._calc_threshold(embeddings)
        )

        model = AgglomerativeClustering(
            None,
            distance_threshold=distance_threshold,
        ).fit(embeddings)

        return model

    def get_labels(self, dataset_path: str):
        embeddings_dict = self._get_embeddings(dataset_path)
        model = self.predict(list(embeddings_dict.values()))
        print(
            f"dataset {dataset_path} has {len(np.unique(model.labels_))} unique speaker labels"
        )

        predicted_path = os.path.join(dataset_path, "predicted.csv")
        if os.path.exists(predicted_path):
            os.remove(predicted_path)

        for i, file in enumerate(tqdm(embeddings_dict.keys())):
            label = str(model.labels_[i])
            append_file(
                predicted_path, f"{os.path.relpath(file, dataset_path)}|{label}\n"
            )

    def _get_embeddings(self, dataset_dir: str):
        datasets = scan_dir(dataset_dir)
        embeddings_dict = {}
        for dataset in datasets:
            embeddings_path = os.path.join(dataset.path, f"{self.method}.csv")
            if os.path.exists(embeddings_path):
                embeddings_dict.update(self.read_embeddings(embeddings_path))
            for name, full_path in [
                (l.name, l.get_audio_path(dataset.wavs_path))
                for l in dataset.transcriptions
                if l.get_audio_path(dataset.wavs_path) not in embeddings_dict.keys()
            ]:
                embedding = get_custom_embedding(full_path, self.method).numpy()
                append_file(embeddings_path, f"{name}|{np.array2string(embedding)}\n")
                embeddings_dict[full_path] = embedding

        return embeddings_dict

    def _calc_threshold(self, embeddings):
        from sklearn.cluster._agglomerative import ward_tree

        _, _, _, _, distances = ward_tree(embeddings, return_distance=True)
        dists_to_check = [x for x in distances if x > 1]
        if len(dists_to_check):
            offset = len(distances) - len(dists_to_check)
            diffs = [
                dists_to_check[i + 1] - x
                for i, x in enumerate(dists_to_check)
                if x < 1.65
            ]
        else:
            offset = 0
            diffs = [
                distances[i + 1] - x
                for i, x in enumerate(distances)
                if i + 1 < len(distances)
            ]
        return distances[offset + np.argmax(diffs)]

    def read_embeddings(self, embeddings_path: str):
        """
        returns dictionary with:
        - keys representing full paths of audio files
        - values representing speaker embedding of audio file
        """

        def np_string2array(string):
            return [
                float(x)
                for x in [
                    x
                    for x in string.replace("]", "").replace("[", "").split(" ")
                    if len(x)
                ]
            ]

        lines = read_lines(embeddings_path)
        return {
            os.path.join(
                os.path.dirname(embeddings_path), "wavs", f"{f}.wav"
            ): np_string2array(e)
            for (f, e) in [l.split("|") for l in lines]
        }


if __name__ == "__main__":
    x = ShmartSpeakerClustering()
    base_dir = "/content"
    for d in os.listdir(base_dir):
        ds_dir = os.path.join(base_dir, d)
        if not os.path.isdir(ds_dir):
            continue
        x.get_labels(ds_dir)
