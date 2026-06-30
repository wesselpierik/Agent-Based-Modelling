from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule
from mesa.visualization.modules import TextElement

# Import the implemented classes
import IPython
import os
import sys

orig_stdout = sys.stdout
sys.stdout = open(os.devnull, "w")
from base_model import BaseModel
from heatmap import HeatmapTile
from police import Police
from thief import Thief
from target import Target
from histogram import HistogramModule

import matplotlib as mpl
import matplotlib.cm as cm
import matplotlib.colors as mcolors

sys.stdout = orig_stdout


def agent_portrayal(agent):
    if isinstance(agent, HeatmapTile):
        x, y = agent.pos
        crime_count = agent.model.crime_heatmap[x][y]

        if crime_count == 0:
            color = "#f7f7f7"
        else:
            norm = mcolors.Normalize(vmin=1, vmax=15)
            cmap = mpl.colormaps.get_cmap("Wistia")
            color = mcolors.to_hex(cmap(norm(crime_count)))

        return {
            "Shape": "rect",
            "Color": color,
            "Filled": "true",
            "Layer": 0,
            "w": 1,
            "h": 1,
        }

    else:
        portrayal = {
            "Shape": "circle",
            "Color": (
                "red"
                if type(agent) is Thief
                else "#6ab956"
                if type(agent) is Target
                else "blue"
            ),
            "Filled": "true",
            "Layer": 1,
            "r": 0.5,
        }
        return portrayal


# Create a grid of 10 by 10 cells, and display it as 500 by 500 pixels
grid = CanvasGrid(agent_portrayal, 100, 100, 500, 500)

# Create a dynamic linegraph
chart = ChartModule(
    [
        {"Label": "Attempts", "Color": "red"},
        {"Label": "Succesful", "Color": "green"},
    ],
    data_collector_name="datacollector",
)

chart2 = ChartModule(
    [
        {"Label": "Avg Attentiveness", "Color": "brown"},
        {"Label": "Avg Riskiness", "Color": "blue"},
    ],
    data_collector_name="datacollector",
)
chart3 = ChartModule(
    [{"Label": "Avg Attentiveness", "Color": "brown"}],
    data_collector_name="datacollector",
)


attentiveness_dist = HistogramModule()

# Create the server, and pass the grid and the graph
server = ModularServer(
    BaseModel,
    [grid, chart, chart2, chart3, attentiveness_dist],
    "BaseModel",
    {"height": 100, "width": 100},
)

server.port = 9003

server.launch()
