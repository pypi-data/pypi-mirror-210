# data.py

"""
Loaders for signal data.
"""


import numpy as np
import os
try:
    from pydub import AudioSegment
    from kymatio.datasets import fetch_fsdd
except ImportError:  # pragma: no cover
    raise ImportError("pydub or kymatio not installed, but can be installed by running "
                      "`pip install topological-signal-compression[extras]`")
import tsc.utils
from typing import List, Tuple


def fsdd(dataset_size: int = 99999, random_seed: int = 0) -> Tuple[List[np.ndarray], List[int]]:
    """
    Collect ``dataset_size`` observations from the Free-Spoken Digit Dataset (FSDD).

    :param dataset_size: number of FSDD records to grab. Default 99999 grabs entire dataset.
    :param random_seed: set a seed to get the same FSDD values each time when sampling a subset.
    :return: ``list`` of arrays of signals and ``list`` of labels corresponding to each array.
    """
    import os
    import scipy.io.wavfile
    info_dataset = fetch_fsdd(verbose=True)
    labels = []
    data = []

    for data_ind in range(len(info_dataset['files'])):
        file_path = os.path.join(info_dataset['path_dataset'],
                                 sorted(info_dataset['files'])[data_ind])
        _, audio_raw = scipy.io.wavfile.read(file_path)

        # to ensure similar lengths, drop coefficients that are too long
        if len(audio_raw) > 8000 or len(audio_raw) < 2000:
            continue

        labels.append(int(file_path.split('/')[-1].split('_')[0]))
        data.append(audio_raw.astype(float))

    if dataset_size > len(data):
        return data, labels

    # randomly collect [dataset_size] number of samples
    rng = np.random.default_rng(random_seed)
    select_indices = sorted(rng.choice(len(data), dataset_size, replace=False))

    data, labels = [data[i] for i in select_indices], [labels[i] for i in select_indices]

    return data, labels


def chopin() -> AudioSegment:
    """
    Pull in 10-second snippet of Chopin (classical music).

    :return: 10 second snippet of music.
    """
    path_to_chopin = os.path.join(tsc.utils.__path__[0], "chopin.mp3")
    return AudioSegment.from_mp3(path_to_chopin)
