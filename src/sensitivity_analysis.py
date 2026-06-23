from IPython.display import clear_output
import SALib
from mesa.batchrunner import BatchRunner
import numpy as np
from SALib.sample import sobol
from base_model import BaseModel
from mesa.batchrunner import FixedBatchRunner
from SALib.analyze import sobol
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations
import os


from tqdm import tqdm

csv_filename = "sensitivity_analysis_results.csv"

import multiprocessing as mp


def evaluate(sample):
    succesful_thieves = np.empty(replicates, dtype=np.int64)
    tk0 = tqdm(range(replicates), total=int(replicates), disable=None)
    for i in tk0:
        model = BaseModel(
            n_police=sample[0],
            loot=sample[1],
            fine=sample[2],
            police_vision_radius=sample[4],
            thief_vision_radius=sample[5],
            police_attentiveness=sample[3],
        )

        for _ in range(max_steps):
            model.step()

        succesful_thieves[i] = model.get_successful_thefts().values[-1]

    return np.mean(succesful_thieves)


if __name__ == "__main__":
    model_class = BaseModel

    problem = {
        "num_vars": 6,
        "names": [
            # "victim_attentiveness",
            "n_police",
            "loot",
            "fine",
            "police_attentiveness",
            "police_vision_radius",
            "thief_vision_radius",
            # "risk",
        ],
        "bounds": [
            # [0.1, 1.0],  # victim attentiveness  (float)
            [1, 20],  # number of police
            [2, 20],  # loot
            [0.2, 7],  # fine
            [0.1, 1.0],  # police attentiveness (float)
            [1, 20],  # vision radius police
            [3, 8],  # vision radius thief
            # [0.1, 1.0],  # risk (float)
        ],
    }

    replicates = 16
    max_steps = 128
    distinct_samples = 16

    X = SALib.sample.sobol.sample(problem, distinct_samples)

    # set the outputs
    model_reporters = {
        "Successful_Thefts": lambda m: m.get_successful_thefts(),
        "Thieves_Caught": lambda m: m.get_caught_thieves(),
    }

    with mp.Pool() as pool:
        Y = pool.map(evaluate, X)

    Si = sobol.analyze(
        problem,
        np.array(Y).flatten(),
        n_processors=16,
        parallel=True,
        print_to_console=True,
    )
