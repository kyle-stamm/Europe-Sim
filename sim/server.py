
import mesa_geo.visualization
import xyzservices.providers as xyz
from mesa.visualization.ModularVisualization import ModularServer
from model import EuropeModel
from mesa.visualization.modules import BarChartModule, ChartModule, TextElement
from mesa.visualization.UserParam import Slider, Checkbox, NumberInput
from technology import *


# defines how agents are portrayed on the map
def agent_portrayal(agent):

    # see cell elevation
    if agent.show_elevation:
        if agent.elevation > 1500:
            portrayal = {"shape": "circle",
                         "color": "Red",
                         "radius": 2,
                         "weight": 1,
                         "description": (round(agent.x, 2), round(agent.y, 2))
                         }
        elif agent.elevation > 1000:
            portrayal = {"shape": "circle",
                         "color": "Orange",
                         "radius": 2,
                         "weight": 1,
                         "description": (round(agent.x, 2), round(agent.y, 2))
                         }
        elif agent.elevation > 500:
            portrayal = {"shape": "circle",
                         "color": "Yellow",
                         "radius": 2,
                         "weight": 1,
                         "description": (round(agent.x, 2), round(agent.y, 2))
                         }
        else:
            portrayal = {"shape": "circle",
                         "color": "Green",
                         "radius": 2,
                         "weight": 1,
                         "description": (round(agent.x, 2), round(agent.y, 2))
                         }

    # see coastal cells
    elif agent.show_coastal:
        if agent.coastal:
            portrayal = {"shape": "circle",
                         "color": "Red",
                         "radius": 2,
                         "weight": 1,
                         "description": (round(agent.x, 2), round(agent.y, 2))
                         }
        else:
            portrayal = {"shape": "circle",
                         "color": "YellowGreen",
                         "radius": 2,
                         "weight": 1,
                         "description": (round(agent.x, 2), round(agent.y, 2))
                         }

    # normal cell display
    elif agent.running or not agent.show_heatmap:

        portrayal = {"shape": "circle",
                     "color": agent.color,
                     "radius": 2,
                     "weight": 1,
                     "description": (round(agent.x, 2), round(agent.y, 2))
                     }

        if len(agent.technology) > 0:
            portrayal["fillOpacity"] = 1
            if isinstance(agent.technology[0], DeltaPowerTechnology):
                portrayal["fillColor"] = "Red"
            elif isinstance(agent.technology[0], AsabiyaTechnology):
                portrayal["fillColor"] = "Green"
            elif isinstance(agent.technology[0], PowerDeclineTechnology):
                portrayal["fillColor"] = "Blue"
            elif isinstance(agent.technology[0], ElevationTechnology):
                portrayal["fillColor"] = "Orange"

    else:
        if agent.times_changed_hands == 0:
            portrayal = {"shape": "circle",
                         "color": "grey",
                         "radius": 2,
                         "weight": 1,
                         "description": (round(agent.x, 2), round(agent.y, 2))
                         }
        elif agent.times_changed_hands > agent.percentiles[3]:
            portrayal = {"shape": "circle",
                         "color": "Red",
                         "radius": 2,
                         "weight": 1,
                         "description": (round(agent.x, 2), round(agent.y, 2))
                         }
        elif agent.times_changed_hands > agent.percentiles[2]:
            portrayal = {"shape": "circle",
                         "color": "Orange",
                         "radius": 2,
                         "weight": 1,
                         "description": (round(agent.x, 2), round(agent.y, 2))
                         }
        elif agent.times_changed_hands > agent.percentiles[1]:
            portrayal = {"shape": "circle",
                         "color": "Yellow",
                         "radius": 2,
                         "weight": 1,
                         "description": (round(agent.x, 2), round(agent.y, 2))
                         }
        elif agent.times_changed_hands > agent.percentiles[0]:
            portrayal = {"shape": "circle",
                         "color": "YellowGreen",
                         "radius": 2,
                         "weight": 1,
                         "description": (round(agent.x, 2), round(agent.y, 2))
                         }
        else:
            portrayal = {"shape": "circle",
                         "color": "Green",
                         "radius": 2,
                         "weight": 1,
                         "description": (round(agent.x, 2), round(agent.y, 2))
                         }

    return portrayal


# text displays
class AvgAreaText(TextElement):
    def render(self, model):
        return f"Average Empire Area (Hexes): {round(model.avg_empire_area, 2)}"


class NumEmpiresText(TextElement):

    def render(self, model):
        return f"Number of Empires: {len([empire for empire in model.empires if empire.size > 5])}"


# creates the line graphs
avg_area_graph = ChartModule([{"Label": "Average Empire Area (Hexes)", "Color": "#750a05"},])
num_empires_graph = ChartModule([{"Label": "Number of Empires", "Color": "#1e85d4"}])

# creates the area histogram
area_histogram = BarChartModule([{"Label": "5-50 Hexes", "Color": "#cc2121"},
                                 {"Label": "51-100 Hexes", "Color": "#db770b"},
                                 {"Label": "101-150 Hexes", "Color": "#e9f022"},
                                 {"Label": "151-200 Hexes", "Color": "#9ddb0b"},
                                 {"Label": "251-300 Hexes", "Color": "#0bbf71"},
                                 {"Label": "301-350 Hexes", "Color": "#06691d"},
                                 {"Label": "351-400 Hexes", "Color": "#0ba1bf"},
                                 {"Label": "401-450 Hexes", "Color": "#0b4abf"},
                                 {"Label": "451-500 Hexes", "Color": "#5c07ab"},
                                 {"Label": "501-550 Hexes", "Color": "#9d07ab"},
                                 {"Label": "550-600 Hexes", "Color": "#ab0782"},
                                 {"Label": "601 or more Hexes", "Color": "#db84c5"}])

# creates the grid from the map module
# can change dimensions of the canvas here if needed
grid = mesa_geo.visualization.MapModule(agent_portrayal, [46, 17], 3.75, tiles=xyz.CartoDB.Positron, map_width=900, map_height=600)

# slider for inputting power decline
power_decline_slider = Slider('Power Decline', value=2, min_value=0.1, max_value=8, step=0.1)
delta_power_slider = Slider('Delta Power', value=0.1, min_value=0.01, max_value=0.2, step=0.01)
asa_growth_slider = Slider('Asabiya Growth', value=0.2, min_value=0.01, max_value=0.3, step=0.01)
asa_decay_slider = Slider('Asabiya Decay', value=0.1, min_value=0.01, max_value=0.3, step=0.01)
elevation_constant_slider = Slider('Elevation Constant', value=4.5, min_value=0, max_value=9, step=0.5)

# number input for setting length of the simulation
sim_length = NumberInput("Length of Simulation (Steps)", value=200)
tech_frequency = NumberInput("Frequency of Technology Drops (0 for no drops)", value=50)

# checkbox for whether to show the heatmap at the end
show_heatmap = Checkbox("Show heatmap at end?", value=False)

# checkboxes to show gis features
show_elevation = Checkbox("Show elevation?", value=False)
show_coastal = Checkbox("Show coastal cells?", value=False)

use_elevation = Checkbox("Elevation Modifier?", value=True)

# dictionary of model parameters to be passed into the server
# can modify with user settable parameters like sliders
model_params = {
    "sim_length": sim_length,
    "tech_frequency": tech_frequency,
    "show_heatmap": show_heatmap,
    "show_elevation": show_elevation,
    "show_coastal": show_coastal,
    "use_elevation": use_elevation,
    "elevation_constant": elevation_constant_slider,
    "power_decline": power_decline_slider,
    "delta_power": delta_power_slider,
    "asa_growth": asa_growth_slider,
    "asa_decay": asa_decay_slider
}

# creates and launches the server
server = ModularServer(EuropeModel, [grid, NumEmpiresText(),  num_empires_graph, AvgAreaText(), avg_area_graph, area_histogram], "Europe Sim", model_params)
server.launch()

