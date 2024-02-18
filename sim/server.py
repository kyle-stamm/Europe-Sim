from mesa.visualization.ModularVisualization import ModularServer
from model import EuropeModel
from mesa.visualization.modules import CanvasHexGrid
from mesa.visualization.UserParam import UserSettableParameter

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
grid = CanvasHexGrid(agent_portrayal, width, height, 10 * width, 10 * height)


model_params = {
    "num_agents": width * height,
    "width": width,
    "height": height
}

server = ModularServer(EuropeModel, [grid], "Europe Sim", model_params)
server.launch()

