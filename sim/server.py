from mesa.visualization.ModularVisualization import ModularServer
from model import EuropeModel
from mesa.visualization.modules import CanvasHexGrid
from mesa.visualization.UserParam import Slider

def agent_portrayal(agent):
    portrayal = {"x": agent.x,
                 "y": agent.y,
                 "Shape": "hex",
                 "Filled": "true",
                 "Color": agent.color,
                 "Layer": 0,
                 "r": 0.9}

    return portrayal


width = 90
height = 60
power_decline = 1.4
grid = CanvasHexGrid(agent_portrayal, width, height, 10 * width, 10 * height)
slider = Slider('Power Decline', value=4, min_value=0.1, max_value=4, step=0.1, description="rate at which empire power declines with distance")

model_params = {
    "power_decline": power_decline,
    "width": width,
    "height": height
}

server = ModularServer(EuropeModel, [grid], "Europe Sim", model_params)
server.launch()

