import SALib
import numpy as np
from SALib.sample import sobol
from base_model import BaseModel
import os
from mpi4py import MPI
from tqdm import tqdm
import multiprocessing as mp

ctx = mp.get_context("spawn")

replicates = 1
max_steps = 50
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


def evaluate(sample: tuple[float, float, float, float, float, float]) -> float:
    succesful_thieves = np.empty(replicates, dtype=np.int64)

    # Create a pretty progress bar
    tk0 = tqdm(range(replicates), total=int(replicates), disable=False)

    # Run the model multiple times
    for i in tk0:
        model = BaseModel(
            n_police=int(sample[0]),
            loot=sample[1],
            fine=sample[2],
            police_vision_radius=sample[4],
            thief_vision_radius=sample[5],
            police_attentiveness=sample[3],
        )

        # Run a single model
        for _ in range(max_steps):
            model.step()

        succesful_thieves[i] = model.get_successful_thefts().values[-1]

    return np.mean(succesful_thieves)


if __name__ == "__main__":
    # MPI setup
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Get all the sample points and spread them through the cluster.
    if rank == 0:
        X = SALib.sample.sobol.sample(problem, distinct_samples)

        chunks = np.array_split(X, size)
    else:
        chunks = None

    # Get the work for each node.
    local_X = comm.scatter(chunks, root=0)

    print(f"Rank {rank}: received {len(local_X)} samples")

    n_workers = int(os.environ.get("SLURM_CPUS_PER_TASK", mp.cpu_count()))

    if rank == 0:
        print(f"Using {n_workers} local workers per node")

    # Run all the models in a Pool of workers.
    with ctx.Pool(processes=n_workers) as pool:
        local_Y = list(pool.imap_unordered(evaluate, local_X))
        print(f"Rank {rank} finished {len(local_Y)} evaluations")

    all_Y = comm.gather(local_Y, root=0)

    if rank == 0:
        Y = np.concat(all_Y)
        print(f"\nCollected {len(Y)} outputs")

        np.savez("all_Y.npz", Y)
        np.savez("all_X.npz", X)

        Si = sobol.analyze(
            problem,
            Y,
            n_processors=16,
            parallel=False,
            print_to_console=True,
        )

        ST = Si["ST"]
        ST_conf = Si["ST_conf"]
        S1 = Si["S1"]
        S1_conf = Si["S1_conf"]
        S2 = Si["S2"]
        S2_conf = Si["S2_conf"]

        with open("sobol_results.txt", "w") as f:
            f.write("=== MODEL SETTINGS ===\n")
            f.write(f"replicates = {replicates}\n")
            f.write(f"max_steps = {max_steps}\n")
            f.write(f"distinct_samples = {distinct_samples}\n\n")

            f.write("=== PROBLEM DEFINITION ===\n")
            f.write(str(problem) + "\n\n")

            f.write("=== SOBOL RESULTS ===\n")
            f.write("ST:\n")
            f.write(str(ST) + "\n")
            f.write("ST_conf:\n")
            f.write(str(ST_conf) + "\n")

            f.write("\nS1:\n")
            f.write(str(S1) + "\n")
            f.write("S1_conf:\n")
            f.write(str(S1_conf) + "\n")

            f.write("\nS2:\n")
            f.write(str(S2) + "\n")
            f.write("S2_conf:\n")
            f.write(str(S2_conf) + "\n")

    comm.Barrier()

    if rank == 0:
        print("Finished\n")
