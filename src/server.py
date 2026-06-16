from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule

# Import the implemented classes
import IPython
import os
import sys

orig_stdout = sys.stdout
sys.stdout = open(os.devnull, 'w')
from base_model import BaseModel, Thief, Victim, Police, HeatmapTile
from histogram import HistogramModule
sys.stdout = orig_stdout


def agent_portrayal(agent):
    if isinstance(agent, HeatmapTile):
        x, y = agent.pos
        crime_count = agent.model.crime_heatmap[x][y]
        
        if crime_count == 0:
            color = "#f0f0f0" 
        elif crime_count <= 1:
            color = "#f9ffa4"
        elif crime_count < 3:
            color = "#e4f500"
        elif crime_count < 6:
            color = "#ffbb00"
        else:
            color = "#fa903a"

            
        return {"Shape": "rect", "Color": color, "Filled": "true", "Layer": 0, "w": 1, "h": 1}
    
    else:
        portrayal = {"Shape": "circle",
                 "Color": "red" if type(agent) is Thief else "green" if type(agent) is Victim else "blue",
                 "Filled": "true",
                 "Layer": 1,
                 "r": 0.5}
        return portrayal

# Create a grid of 10 by 10 cells, and display it as 500 by 500 pixels
grid = CanvasGrid(agent_portrayal, 50, 50, 500, 500)

# Create a dynamic linegraph
chart = ChartModule([{"Label": "Attempts",
                      "Color": "red"},
                      {"Label": "Succesful",
                      "Color": "green"},],
                    data_collector_name='datacollector')

chart2 = ChartModule([{"Label": "Avg Attentiveness",
                       "Color": "brown"},
                      {"Label": "Avg Riskyness",
                       "Color": "blue"},],
                    data_collector_name='datacollector')

attentiveness_dist = HistogramModule()

# Create the server, and pass the grid and the graph
server = ModularServer(BaseModel,
                       [grid,chart, chart2, attentiveness_dist],
                       "BaseModel",
                       {})

server.port = 9042

server.launch()
