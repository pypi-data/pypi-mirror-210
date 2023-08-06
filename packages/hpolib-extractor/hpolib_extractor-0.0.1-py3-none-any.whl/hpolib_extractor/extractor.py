import itertools
import json
import os
import pickle
from typing import List

import h5py

import numpy as np

from tqdm import tqdm


SEARCH_SPACE = {
    "init_lr": [5e-4, 1e-3, 5e-3, 1e-2, 5e-2, 1e-1],
    "lr_schedule": ["cosine", "const"],
    "batch_size": [8, 16, 32, 64],
    "activation_fn_1": ["relu", "tanh"],
    "activation_fn_2": ["relu", "tanh"],
    "dropout_1": [0.0, 0.3, 0.6],
    "dropout_2": [0.0, 0.3, 0.6],
    "n_units_1": [16, 32, 64, 128, 256, 512],
    "n_units_2": [16, 32, 64, 128, 256, 512],
}
DATASET_NAMES = ["slice_localization", "protein_structure", "naval_propulsion", "parkinsons_telemonitoring"]
N_ENTRIES = np.prod([len(vs) for vs in SEARCH_SPACE.values()])


class HPOLibExtractor:
    def __init__(self, dataset_id: int, data_dir: str, epochs: List[int] = [100]):
        self._dataset_name = DATASET_NAMES[dataset_id]
        path = os.path.join(data_dir, f"fcnet_{self._dataset_name}_data.hdf5")
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"{path} does not exist. Please make sure that you already download and "
                f"locate the datasets at {path}"
            )

        self._db = h5py.File(path, "r")
        epoch_array = np.array(epochs)
        if not np.all((1 <= epoch_array) & (epoch_array) <= 100):
            raise ValueError("Epoch must be in [1, 100].")

        self._epochs_id = [e - 1 for e in np.sort(epochs)]
        self._collected_data = {}

    @property
    def dataset_name(self) -> str:
        return self._dataset_name

    def collect(self) -> None:
        # max_epoch: 99, min_epoch: 0
        loss_key = "valid_mse"
        runtime_key = "runtime"
        n_seeds = 4
        for it in tqdm(itertools.product(*(list(v) for v in SEARCH_SPACE.values())), total=N_ENTRIES):
            config = {k: v for k, v in zip(SEARCH_SPACE.keys(), it)}
            key = json.dumps(config, sort_keys=True)
            target_data = self._db[key]
            self._collected_data[key] = {
                loss_key: [{e: float(target_data[loss_key][s][e]) for e in self._epochs_id} for s in range(n_seeds)],
                runtime_key: [float(target_data[runtime_key][s]) for s in range(n_seeds)],
            }


def extract(data_dir: str, epochs: List[int]):
    for i in range(4):
        extractor = HPOLibExtractor(dataset_id=i, epochs=epochs, data_dir=data_dir)
        print(f"Start extracting {extractor.dataset_name}")
        extractor.collect()
        pkl_path = os.path.join(data_dir, f"{extractor.dataset_name}.pkl")
        pickle.dump(extractor._collected_data, open(pkl_path, "wb"))
