from IPython.display import clear_output
import SALib
from mesa.batchrunner import BatchRunner
import pandas as pd
import numpy as np
from SALib.sample import saltelli
from base_model import BaseModel
from mesa.batchrunner import FixedBatchRunner
from SALib.analyze import sobol
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations


model_class = BaseModel

problem = {
    'num_vars': 4,
    'names': ['victim_attentiveness', 'police_attentiveness', 'vision_radius', 'risk' ],
    'bounds': [
        [0.1, 1.0],   # victim attentiveness  (float)
        [0.1, 1.0],   # police attentiveness (float)
        [1, 20],       # vision radius
        [1.0, 1.0]    # risk (float)
    ]
}

replicates = 10
max_steps = 100
distinct_samples = 10

param_values = saltelli.sample(problem, distinct_samples)

# set the outputs
model_reporters = {
    "Successful_Thefts": lambda m: m.successful_thefts, 
    "Thieves_Caught": lambda m: m.thieves_caught
}



data = {}

for i, var in enumerate(problem['names']):
    # Get the bounds for this variable and get <distinct_samples> samples within this space (uniform)
    samples = np.linspace(*problem['bounds'][i], num=distinct_samples)
    
    # Keep in mind that wolf_gain_from_food should be integers. You will have to change
    # your code to acommodate for this or sample in such a way that you only get integers.
    if var == 'wolf_gain_from_food':
        samples = np.linspace(*problem['bounds'][i], num=distinct_samples, dtype=int)
    
    batch = FixedBatchRunner(BaseModel,
                        max_steps=max_steps,
                        iterations=replicates,
                        parameters_list=[{var: value} for value in samples],
                        fixed_parameters= None,
                        model_reporters=model_reporters,
                        display_progress=True)
    
    batch.run_all()
    
    data[var] = batch.get_model_vars_dataframe()