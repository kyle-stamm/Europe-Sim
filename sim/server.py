
# hella modules
import mesa.visualization
import mesa_geo.visualization
from mesa.visualization.ModularVisualization import ModularServer
from model import EuropeModel
import xyzservices.providers as xyz
from mesa.visualization.modules import BarChartModule
from mesa.visualization.modules import ChartModule
from mesa.visualization.modules import TextElement
from mesa.visualization.UserParam import Slider


# defines how agents are portrayed on the map
def agent_portrayal(agent):

    # dictionary of portrayal parameters
    portrayal = {"shape": "circle",
                 "color": agent.color,
                 "radius": 0.001
                 }

    return portrayal


# text displays
class AvgAreaText(TextElement):
    def render(self, model):
        return f"Average Empire Area: {round(model.avg_empire_area, 2)}"


class NumEmpiresText(TextElement):

    def render(self, model):
        return f"Total Number of Empires: {len(model.empires)}"


class NumBigEmpiresText(TextElement):

    def render(self, model):
        return f"Number of Empires with more than 5 hexes: {len([empire for empire in model.empires if empire.size > 5])}"


class NumSmallEmpiresText(TextElement):

    def render(self, model):
        return f"Number of Empires with less than 5 hexes: {len([empire for empire in model.empires if empire.size < 5])}"


avg_area_text = AvgAreaText()
num_empires_text = NumEmpiresText()
num_big_empires_text = NumBigEmpiresText()
num_small_empires_text = NumSmallEmpiresText()

# creates the line graphs
avg_area_graph = ChartModule([{"Label": "average empire area", "Color": "Black"},])
num_empires_graph = ChartModule([{"Label": "number of empires with more than 5 hexes", "Color": "IndianRed"}])

# creates the area histogram
area_histogram = BarChartModule([{"Label": "5-50 Hexes", "Color": "IndianRed"},
                                 {"Label": "51-100 Hexes", "Color": "Magenta"},
                                 {"Label": "101-150 Hexes", "Color": "Olive"},
                                 {"Label": "151-200 Hexes", "Color": "Maroon"},
                                 {"Label": "251-300 Hexes", "Color": "Blue"},
                                 {"Label": "301-350 Hexes", "Color": "Gold"},
                                 {"Label": "351-400 Hexes", "Color": "DarkGreen"},
                                 {"Label": "401-450 Hexes", "Color": "DeepPink"},
                                 {"Label": "451-500 Hexes", "Color": "LightBlue"},
                                 {"Label": "501-550 Hexes", "Color": "DarkBlue"},
                                 {"Label": "550-600 Hexes", "Color": "Orange"},
                                 {"Label": "601 or more Hexes", "Color": "Purple"}])

# creates the grid from the map module
# can change dimensions of the canvas here if needed
grid = mesa_geo.visualization.MapModule(agent_portrayal, [46, 17], 3.75, tiles=xyz.CartoDB.Positron, map_width=900, map_height=600)
slider = Slider('Power Decline', value=1.4, min_value=0.1, max_value=4, step=0.1, description="rate at which empire power declines with distance")

# dictionary of model parameters to be passed into the server
# can modify with user settable parameters like sliders
model_params = {
    "power_decline": slider
}

# creates and launches the server
server = ModularServer(EuropeModel, [grid, num_big_empires_text, num_small_empires_text, num_empires_text,  num_empires_graph, avg_area_text, avg_area_graph, area_histogram], "Europe Sim", model_params)
server.launch()

