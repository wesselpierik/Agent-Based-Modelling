from IPython.display import clear_output
import SALib
from mesa.batchrunner import BatchRunner
import numpy as np
from SALib.sample import saltelli
from base_model import BaseModel
from mesa.batchrunner import FixedBatchRunner
from SALib.analyze import sobol
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations
import os


model_class = BaseModel

problem = {
    'num_vars': 4,
    'names': [
        'n_police',               # Matches your model's police parameter (Integer)
        'decay_attentiveness',    # Matches delta_A (Float)
        'increase_attentiveness', # Matches alpha (Float)
        'increase_riskiness'      # Matches beta (Float)
    ],
    'bounds': [
        [1, 30],       # n_police bounds (baseline: 5)
        [0.01, 0.3],   # decay_attentiveness bounds (baseline: 0.1)
        [0.1, 0.9],    # increase_attentiveness bounds (baseline: 0.5)
        [0.01, 0.2]    # increase_riskiness bounds (baseline: 0.05)
    ]
}

replicates = 10
max_steps = 100
distinct_samples = 16  # 2^4 

# Generate the parameter sample matrix
param_values = sobol.sample(problem, distinct_samples)

# Unpack the generated array into a structured list of dictionaries
parameters_list = []
for row in param_values:
    param_dict = {}
    for i, var_name in enumerate(problem['names']):
        val = row[i]
        
        # n_police must be integer
        if var_name == 'n_police': 
            val = int(np.round(val))
            
        param_dict[var_name] = val
    parameters_list.append(param_dict)

# Define outputs
model_reporters = {
    "Avg_Successful_Thefts": lambda m: (
        sum([a.succesful_steals for a in m.schedule_Thief.agents]) / m.n_thieves 
        if m.n_thieves > 0 else 0
    ), 
    "Avg_Attempted_Thefts": lambda m: (
        sum([a.attempts for a in m.schedule_Thief.agents]) / m.n_thieves 
        if m.n_thieves > 0 else 0
    )
}

csv_filename = "sensitivity_analysis_results.csv"

# Remove old results if restarting fresh
if os.path.exists(csv_filename):
    os.remove(csv_filename)

for idx, params in enumerate(parameters_list):
    batch = FixedBatchRunner(
        BaseModel,
        max_steps=max_steps,
        iterations=replicates,
        parameters_list=[params], 
        fixed_parameters={
            'width': 50,
            'height': 50,
            'num_targets': 1500,
            'baseline_decay_prob': 0.01,
            'decrease_riskiness': 0.09
        },
        model_reporters=model_reporters,
        display_progress=True
    )
    
    # Run the iterations for this specific configuration block
    batch.run_all()
    
    # Extract the results and add to csv file
    results = batch.get_model_vars_dataframe()
    results.to_csv(csv_filename, mode='a', index=False, header=not os.path.exists(csv_filename))