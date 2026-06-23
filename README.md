# Agent-based Modelling

## Group: 15
* Finn Dokter (13680706)
* Anna van Dun (14535734)
* Luca van der Nooij
* Wessel Pierik

## Project motivation

## Short project summary

## Libraries
For the required dependencies, and their versions, see pyproject.toml.

## Structure
### Source Python files
#### src/base_model.py
Initialise parameters, create agents, set up the data collector and run the model.

#### src/heatmap.py
Create the heat map to visualise where pickpocketing events happen.

#### src/person.py
Functions for general movement of an agent.

#### src/police.py (TODO maybe: change to src/guardian.py)
Initialise guardian parameters and compute steps for guardian agents.

#### src/victim.py (TODO: change to src/target.py)
Initialise target parameters and compute steps for target agents.

#### src/thief.py (TODO: src/offender.py)
Initialise offender parameters and compute steps for offender agents.

#### src/server.py
File for the visualisation of the simulation. It shows the grid per time step and the resulting time-dependent graphs.

#### src/sensitivity_analysis.py

<!-- ### Results and visualisation files -->

## Usage
To install the uv environment, 

To use the uv environment, type:

```uv sync```

To run the simulation, use:

```uv run src/server.py```

You will then be directed to an external browser, where the simulation can be run, and the resulting time-dependent graphs are shown. Before running the simulation, the number of frames per second can be specified through a slider. The simulation can be started, stopped and reset using the ```start```, ```stop``` and ```reset``` buttons, respectively. A single step can be computed using the ```step``` button.

The first graph shows the number of stealing attempts (red) and succesful attempts (green) as a function of time steps.
The second graph shows the average attentiveness of the targets (red) and the average riskiness of the offenders (blue) as a function of time steps.

To run the sensitivity analysis, use:

```uv run src/sensitivity_analysis.py```

## Important parameters (TODO: update parameters)
* Number of targets (): 1500
* Number of offenders (): 10
* Number of guardians (): 5
* Grid size (): 50
* Guardian vision radius (): 8
* Offender vision radius (): 3
* Victim vision radius (): 1
* Increase attentiveness ($\alpha$): 0.5
* Increase riskiness ($\beta$): 0.05
* Decay attentiveness ($\delta$): 0.1

## Aknowledgements
* Wolf-sheep model: 
* Sensitivity analysis: 