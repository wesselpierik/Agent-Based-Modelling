from base_model import BaseModel
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations
import os
from mpi4py import MPI
from tqdm import tqdm
import multiprocessing as mp

replicates = 8
max_steps = 500

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
        [1, 20],  # vision radius thief
        # [0.1, 1.0],  # risk (float)
    ],
}

parameter_names = [
    "n_police",
    "loot",
    "fine",
    "police_attentiveness",
    "police_vision_radius",
    "thief_vision_radius",
]

bounds = [
    (1, 32),  # number of police
    (2, 20),  # loot
    (0.2, 20),  # fine
    (0.1, 1.0),  # police attentiveness (float)
    (1, 20),  # vision radius police
    (1, 20),  # vision radius thief
]

param_bounds_dict = {name: bound for name, bound in zip(parameter_names, bounds)}

baseline = {
    "n_police": 10,
    "loot": 5,
    "fine": 2,
    "police_attentiveness": 0.8,
    "police_vision_radius": 8,
    "thief_vision_radius": 3,
}


def evaluate(args):
    succesful_thieves = np.empty(replicates, dtype=np.int64)

    sample, x_name, y_name = args

    params = baseline.copy()

    params[x_name] = sample[0]
    params[y_name] = sample[1]

    params["n_police"] = int(round(params["n_police"]))
    params["police_vision_radius"] = int(round(params["police_vision_radius"]))
    params["thief_vision_radius"] = int(round(params["thief_vision_radius"]))

    for i in range(replicates):
        model = BaseModel(**params)

        for _ in range(max_steps):
            model.step()

        succesful_thieves[i] = model.get_successful_thefts().values[-1]

    return np.mean(succesful_thieves)


def mesh_grid_generation(x_vals_name, y_vals_name, n_grid):
    x_bounds = param_bounds_dict[x_vals_name]
    y_bounds = param_bounds_dict[y_vals_name]

    x_vals = np.linspace(*x_bounds, n_grid)
    y_vals = np.linspace(*y_bounds, n_grid)

    P1, P2 = np.meshgrid(x_vals, y_vals)

    X = np.column_stack([P1.ravel(), P2.ravel()])

    n_workers = int(os.environ.get("SLURM_CPUS_PER_TASK", mp.cpu_count()))

    tasks = [(sample, x_vals_name, y_vals_name) for sample in X]

    with mp.Pool(processes=n_workers) as pool:
        chunksize = max(1, len(tasks) // n_workers)
        results_iter = pool.imap(evaluate, tasks, chunksize=chunksize)

        Y = []

        for y in tqdm(
            results_iter,
            total=len(X),
            desc=f"Rank {rank} evaluating",
            dynamic_ncols=True,
        ):
            Y.append(y)

    Y_grid = np.asarray(Y).reshape(n_grid, n_grid)

    plt.figure(figsize=(7, 6))

    plt.contourf(P1, P2, Y_grid, levels=400, cmap="viridis")

    plt.colorbar(label="Successful thefts")

    plt.xlabel(x_vals_name)
    plt.ylabel(y_vals_name)
    plt.title("Successful thefts for different parameter pairs")

    try:
        os.mkdir("heatmaps")
    except FileExistsError:
        pass

    try:
        os.mkdir("raw_data")
    except FileExistsError:
        pass

    plt.savefig(f"heatmaps/{x_vals_name} vs {y_vals_name}.png", bbox_inches="tight")

    np.savez(
        f"raw_data/{x_vals_name} {y_vals_name} {n_grid} {replicates} {max_steps}.npz", {"Y_grid": Y_grid}
    )


if __name__ == "__main__":
    # MPI setup
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    pairs = list(combinations(parameter_names, 2))

    local_pairs = [pair for i, pair in enumerate(pairs) if i % size == rank]

    n_grid = 20  # resolution of sweep

    for x_name, y_name in local_pairs:
        mesh_grid_generation(x_name, y_name, n_grid)

    comm.Barrier()

    if rank == 0:
        print("Finished\n")
