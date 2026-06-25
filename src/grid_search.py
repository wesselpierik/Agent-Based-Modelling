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

from mpi4py import MPI


from tqdm import tqdm

csv_filename = "sensitivity_analysis_results.csv"

import multiprocessing as mp

ctx = mp.get_context("spawn")

replicates = 8
max_steps = 500
distinct_samples = 4

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
        [1, 32],  # number of police
        [2, 20],  # loot
        [0.2, 7],  # fine
        [0.1, 1.0],  # police attentiveness (float)
        [1, 20],  # vision radius police
        [3, 8],  # vision radius thief
        # [0.1, 1.0],  # risk (float)
    ],
}


def evaluate(sample):
    succesful_thieves = np.empty(replicates, dtype=np.int64)

    for i in range(replicates):

        n_police = int(sample[0])
        thief_vision_radius = sample[1]

        model = BaseModel(
            n_police=n_police,
            loot=5,  # FIXED (choose baseline)
            fine=2,  # FIXED
            police_vision_radius=8,  # FIXED
            thief_vision_radius=thief_vision_radius,
            police_attentiveness=0.8,  # FIXED
        )

        for _ in range(max_steps):
            model.step()

        succesful_thieves[i] = model.get_successful_thefts().values[-1]

    return np.mean(succesful_thieves)


if __name__ == "__main__":
    # MPI setup
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    if rank == 0:
        n_grid = 20  # resolution of sweep

        n_police_vals = np.linspace(1, 32, n_grid)
        thief_vision_vals = np.linspace(3, 8, n_grid)

        P1, P2 = np.meshgrid(n_police_vals, thief_vision_vals)

        X = np.column_stack([P1.ravel(), P2.ravel()])

        chunks = np.array_split(X, size)
    else:
        chunks = None

    local_X = comm.scatter(chunks, root=0)

    print(f"Rank {rank}: received {len(local_X)} samples")

    n_workers = int(os.environ.get("SLURM_CPUS_PER_TASK", mp.cpu_count()))

    if rank == 0:
        print(f"Using {n_workers} local workers per node")

    with ctx.Pool(processes=n_workers) as pool:
        # tqdm wrapper around iterator
        results_iter = pool.imap_unordered(evaluate, local_X)

        local_Y = []

        for y in tqdm(
            results_iter,
            total=len(local_X),
            desc=f"Rank {rank} evaluating",
            dynamic_ncols=True,
        ):
            local_Y.append(y)

    all_Y = comm.gather(local_Y, root=0)

    if rank == 0:
        Y = np.concat(all_Y)
        Y_grid = Y.reshape(n_grid, n_grid)

        plt.figure(figsize=(7, 6))

        plt.contourf(P1, P2, Y_grid, levels=400, cmap="viridis")

        plt.colorbar(label="Successful thefts")

        plt.xlabel("n_police")
        plt.ylabel("thief_vision_radius")
        plt.title("Response surface")

        plt.savefig("n_police vs thief vision.png", bbox_inches="tight")

    comm.Barrier()

    if rank == 0:
        print("Finished\n")
