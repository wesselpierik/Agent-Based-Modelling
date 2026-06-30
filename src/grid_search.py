from base_model import BaseModel
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations
import os
from mpi4py import MPI
from tqdm import tqdm
import multiprocessing as mp

"""
WARNING: THIS FILE WILL ONLY WORK CORRECTLY ON A SLURM CONTROLLED
SUPERCOMPUTER.
A LAPTOP WILL NOT BE ABLE TO MAKE MULTIPLE MPI NODES AND ALSO MULTIPROCESS FOR
EACH MPI NODE.

ON LINUX THIS WILL RESULT IN A FORK CRASH. SINCE THE WORKLOAD IS HIGH, THE
ATTEMPT IS NOT RECOMMENDED ANYWAY.
"""

replicates = 8
max_steps = 500

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

param_bounds_dict = {
    name: bound for name, bound in zip(parameter_names, bounds)
}

baseline = {
    "n_police": 10,
    "loot": 5,
    "fine": 2,
    "police_attentiveness": 0.8,
    "police_vision_radius": 8,
    "thief_vision_radius": 3,
}


def evaluate(args: tuple[tuple[float | int, float | int], str, str]) -> float:
    """
    Evaluate a single combination of parameters replicates number of times.
    The combination of parameters should be given to args as a tuple of
    ((x_value, y_value), x_parameter_name, y_parameter_name).

    Args:
        args: A tuple containing a tuple of parameter settings and the
              corresponing variable names.

    Returns:
        The mean number of successful thefts
    """
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


def mesh_grid_generation(
    x_vals_name: str, y_vals_name: str, n_grid: int
) -> None:
    """
    Generate the heatmap for a single combination of parameters x_vals_name and
    y_vals_name. The number of sample points for each parameter is equal to
    n_grid.

    Args:
        x_vals_name: The name of the parameter that is plotted on the x-axis.
        y_vals_name: The name of the parameter that is plotted on the y-axis.
        n_grid: The number of subdivisions in the range of both parameters.
    """
    x_bounds = param_bounds_dict[x_vals_name]
    y_bounds = param_bounds_dict[y_vals_name]

    x_vals = np.linspace(*x_bounds, n_grid)
    y_vals = np.linspace(*y_bounds, n_grid)

    P1, P2 = np.meshgrid(x_vals, y_vals)

    X = np.column_stack([P1.ravel(), P2.ravel()])

    n_workers = int(os.environ.get("SLURM_CPUS_PER_TASK", mp.cpu_count()))

    # Create all the required sample points.
    tasks = [(sample, x_vals_name, y_vals_name) for sample in X]

    # Run all required models
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

    # Process the results into a heatmap
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

    plt.savefig(
        f"heatmaps/{x_vals_name} vs {y_vals_name}.png", bbox_inches="tight"
    )

    np.savez(
        f"raw_data/{x_vals_name} {y_vals_name} {n_grid} {replicates} {max_steps}.npz",
        {"Y_grid": Y_grid},
    )


if __name__ == "__main__":
    # MPI setup
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Get all the pair combination of parameters
    pairs = list(combinations(parameter_names, 2))

    # Filter the pairs for each MPI node
    local_pairs = [pair for i, pair in enumerate(pairs) if i % size == rank]

    n_grid = 20  # resolution of sweep

    # Sweep the model
    for x_name, y_name in local_pairs:
        mesh_grid_generation(x_name, y_name, n_grid)

    # Wait for all models to finish
    comm.Barrier()

    # Final message
    if rank == 0:
        print("Finished\n")
