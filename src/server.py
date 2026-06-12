from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule

# Import the implemented classes
import IPython
import os
import sys

# Change stdout so we can ignore most prints etc.
orig_stdout = sys.stdout
sys.stdout = open(os.devnull, 'w')
# IPython.get_ipython().magic("base_model.py")
from base_model import BaseModel, Thief, Victim, Police
sys.stdout = orig_stdout

# You can change this to whatever ou want. Make sure to make the different types
# of agents distinguishable
def agent_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Color": "red" if type(agent) is Thief else "green" if type(agent) is Victim else "blue",
                 "Filled": "true",
                 "Layer": 0,
                 "r": 0.5}
    return portrayal

# Create a grid of 10 by 10 cells, and display it as 500 by 500 pixels
grid = CanvasGrid(agent_portrayal, 100, 100, 500, 500)

# # Create a dynamic linegraph
# chart = ChartModule([{"Label": "Thieves",
#                       "Color": "red"},
#                       {"Label": "Victims",
#                       "Color": "green"},
#                       {"Label": "Police",
#                       "Color": "blue"}],
#                     data_collector_name='datacollector')

# Create the server, and pass the grid and the graph
server = ModularServer(BaseModel,
                       [grid],
                       "BaseModel",
                       {})

server.port = 9026

server.launch()
