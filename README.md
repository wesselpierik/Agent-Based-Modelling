# Agent-based Modelling

## Group: 15
* Finn Dokter (13680706)
* Anna van Dun (14535734)
* Luca van der Nooij (14026554)
* Wessel Pierik (14445662)


## Project motivation
In the field of criminology, agent-based models are a relatively new method of simulating crimes. Pickpocketing, the act of stealing another person's belongings in a public space, is a widespread problem, especially in highly touristic spaces. A pickpocket might decide to steal from someone depending on their observations, for example, whether there is a police officer nearby or the perceived wealth of the pickpocket's target. The main goal of this research is to look at the influence of such parameters on the success and frequency of pickpocketing events.

## Short project summary
The model contains three agents: pickpockets, potential victims and police officers. The environment is a discretised lattice. Each lattice cell can contain one ageny, and a thief agent can attempt a pickpocketing event when a target agent is within the Moore neighbourhood of the pickpocket. As stated before, the probability that a pickpocketing attempt is made is dependent on a number of parameters, which are dependent on the agents.

The movement of the are varied. In general, each agent will move one lattice cell at each time step. If a passer-by is successfully pick-pocketed, their attentiveness will increase, and they will move close to a police officer. A thief moves towards crowds, and if he is caught, he gets more cautious. Police move in patrols up and down the grid.

An agent-based Model is the best technique for the project, because it supports both heterogeneity and spatial dependence by allowing individual agents to interact locally with each other and their environment.


## Libraries
For the required dependencies, and their versions, see pyproject.toml.

## Structure
### Source Python files
#### src/base_model.py
Initialise parameters, create agents, set up the data collector and run the model.

#### src/grid_search.py
Searches the entire parameter space for all 6 parameters between the bounds.
This process is heavy to run and will not run on laptops (Linux Ubuntu confirmed/Windows and macOS are not tested). It is specifically written to get the best performance from the Snellius supercomputer.

#### src/heatmap.py
Create the heat map to visualise where pickpocketing events happen.

#### src/person.py
Functions for general movement of an agent.

#### src/police.py
Initialise police parameters and compute steps for police agents.

#### src/target.py
Initialise target parameters and compute steps for target agents.

#### src/thief.py
Initialise thief parameters and compute steps for thief agents.

#### src/server.py
File for the visualisation of the simulation. It shows the grid per time step and the resulting time-dependent graphs.

#### src/sensitivity_analysis.py
This file runs the sensitivity analysis and writes the results to sobol_results.txt.

#### src/sensitivity_plot.py
This file processes the output from the sensitivity analysis and creates the sensitivity plot. Requires an OpenMPI installation to run.

## Usage
To install the uv environment, 

To use the uv environment, type:

```uv sync```

To run the simulation, use:

```uv run src/server.py```

You will then be directed to an external browser, where the simulation can be run, and the resulting time-dependent graphs are shown. Before running the simulation, the number of frames per second can be specified through a slider. The simulation can be started, stopped and reset using the ```start```, ```stop``` and ```reset``` buttons, respectively. A single step can be computed using the ```step``` button.

The first graph shows the number of stealing attempts (red) and succesful attempts (green) as a function of time steps.
The second graph shows the average attentiveness of the targets (red) and the average riskiness of the offenders (blue) as a function of time steps. The third graph shows the current distribution of attentiveness among the target agents.

To run the sensitivity analysis, use:

```uv run src/sensitivity_analysis.py```

## Important baseline parameters 
* Grid size (width, height): 50 x 50
* Number of offenders (n_thieves): 10
* Number of targets (n_targets): 1500
* Number of guardians (n_police): 10
* Guardian vision radius (police_vision_radius): 8
* Offender vision radius (thief_vision_radius): 3
* Increase attentiveness (increase_attentiveness): 0.5
* Increase riskiness (increase_riskiness): 0.05
* Decay attentiveness (decay_attentiveness): 0.1
* Decay riskiness (decay_riskiness): 0.5
* Guardian attentiveness (police_attentiveness) = 0.8
* Thief loot after sucessful steal (loot): 5
* Thief fine after being caught (fine): 2


## Aknowledgements
* Wolf-sheep model: We have used the notebook from the first assignment to guide us on how to set up a model using the mesa package. Similarly, we have used the server.py file to figure out how to show our simulation.
* Sensitivity analysis: We have used the given sensitivity analysis notebook to figure out how to apply the sensistivity analysis in Python.