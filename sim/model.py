
# 863 km^2
# diffusion of innovation
# muskets -> delta power
# saddles -> power_decline
# siege tech -> elevation
# printing press -> asabiya
# cesare marchetti

# aggressive vs defensive cells
# moralizing single god vs. many gods
# give every cell an elevation tech

import geopandas as gpd
import math
import mesa
import mesa_geo as mg
import random
from mesa import DataCollector
from numpy import percentile

from cell import EmpireCell
from empire import Empire
from technology import *
from religion import *


# model class
class EuropeModel(mesa.Model):

    hex_to_meters = 863000000
    tech_types = ["Asabiya Growth", "Asabiya Decay", "Power Decline", "Delta Power", "Elevation"]

    def __init__(self, power_decline=4, sim_length=200, delta_power=0.1,
                 asa_growth=0.2, asa_decay=0.1, elevation_constant=6.5, tech_frequency=0,
                 use_elevation=True, agent_reporters=True, use_warmup=False, batch_run=True,
                 show_heatmap=False, show_elevation=False, show_coastal=False):
        super().__init__()

        # power decline is determined by the UI slider
        self.power_decline = power_decline

        # initial global variables
        # determined by UI slider
        self.delta_power = delta_power
        self.asa_growth = asa_growth
        self.asa_decay = asa_decay

        self.delta_power_change = delta_power

        self.techs_dropped = []
        self.tech_frequency = tech_frequency

        # sim length is determined by user input
        self.sim_length = sim_length

        # counts steps since the model began running
        self.steps = 0

        # tracks whether the simulation is running
        self.running = True

        # stores whether the simulation shows the heatmap at the end of its runtime
        self.show_heatmap = show_heatmap

        self.show_elevation = show_elevation
        self.show_coastal = show_coastal
        self.agent_reporters = agent_reporters

        self.use_elevation = use_elevation
        self.elevation_constant = 10 - elevation_constant

        self.batch_run = batch_run

        self.differences = []
        self.avg_difference = 0

        # sets schedule to be random activation so as not to favor one empire
        self.schedule = mesa.time.RandomActivation(self)

        # list of empires currently in the model
        self.empires = []
        self.religions = []

        self.default_religion = Religion(0)
        self.default_religion.type = "non-pros"
        self.default_religion.tolerance = 1.5
        self.default_religion.conversion = 0

        # default empire that all cells start as a part of
        self.default_empire = Empire(0, self)
        self.default_empire.color = "grey"

        self.avg_empire_area = 0
        self.avg_empire_elevation = 0

        # area histogram
        # each element is a frequency bar
        self.area_histogram = [0 for x in range(13)]

        # data collector
        # format is {<datapoint name>: lambda model: model.<reporting function or variable>, ...}
        if self.agent_reporters:
            self.datacollector = DataCollector(model_reporters={"starting x": lambda model: model.starting_x,
                                                                "starting y": lambda model: model.starting_y,
                                                                "steps": lambda model: model.steps,
                                                                "Average Empire Area (Hexes)": lambda model: model.avg_empire_area,
                                                                "Average Empire Area (m^2)": lambda model: model.avg_empire_area * self.hex_to_meters,
                                                                "Number of Empires": lambda model: len([empire for empire in model.empires if empire.size > 5]),
                                                                "Elevation Constant": lambda model: model.elevation_constant},
                                               agent_reporters={"Elevation": lambda agent: agent.elevation,
                                                                "Times Changed Hands": lambda agent: agent.times_changed_hands + 0.0001})
        else:
            self.datacollector = DataCollector(model_reporters={"starting x": lambda model: model.starting_x,
                                                                "starting y": lambda model: model.starting_y,
                                                                "steps": lambda model: model.steps,
                                                                "Average Empire Area (Hexes)": lambda model: model.avg_empire_area,
                                                                "Average Empire Area (m^2)": lambda model: model.avg_empire_area * self.hex_to_meters,
                                                                "Number of Empires": lambda model: len([empire for empire in model.empires if empire.size > 5]),
                                                                "Average Empire Elevation": lambda model: model.avg_empire_elevation,
                                                                "Average Power Difference": lambda model: model.avg_difference,
                                                                "5-50 Hexes": lambda model: model.area_histogram[0],
                                                                "51-100 Hexes": lambda model: model.area_histogram[1],
                                                                "101-150 Hexes": lambda model: model.area_histogram[2],
                                                                "151-200 Hexes": lambda model: model.area_histogram[3],
                                                                "201-250 Hexes": lambda model: model.area_histogram[4],
                                                                "251-300 Hexes": lambda model: model.area_histogram[5],
                                                                "301-350 Hexes": lambda model: model.area_histogram[6],
                                                                "351-400 Hexes": lambda model: model.area_histogram[7],
                                                                "401-450 Hexes": lambda model: model.area_histogram[8],
                                                                "451-500 Hexes": lambda model: model.area_histogram[9],
                                                                "501-550 Hexes": lambda model: model.area_histogram[10],
                                                                "551-600 Hexes": lambda model: model.area_histogram[11],
                                                                "601 or more Hexes": lambda model: model.area_histogram[12],
                                                                "Elevation Constant": lambda model: model.elevation_constant})

        # creates the geo space with the GeoJSON coordinate system
        self.space = mg.GeoSpace(crs="epsg:4326", warn_crs_conversion=False)

        # agent generator
        ac = mg.AgentCreator(EmpireCell, model=self)

        # creates cells from the GeoJSON data file
        gdf = gpd.read_file("gis_data/hex_with_elevation.geojson")
        self.cells = ac.from_GeoDataFrame(gdf)

        # adds those agents to the geo space
        self.space.add_agents(self.cells)

        # adds all new cells to the default empire
        # also adds them to the scheduler
        for cell in self.cells:
            cell.elevation *= 100
            self.default_empire.add_cell(cell)
            self.schedule.add(cell)
            cell.setup_neighbors()
            if self.show_heatmap:
                cell.show_heatmap = True

            if self.show_coastal:
                cell.show_coastal = True

            if self.show_elevation:
                cell.show_elevation = True

        # spaghetti code to fix coastal cells
        for cell in [cell for cell in self.cells if cell.coastal]:
            cell.fix_coastal()

        # sets up the initial empire

        # picks a random cell
        starting_cells = [self.cells[random.randint(0, len(self.cells) - 1)]]
        self.starting_x = starting_cells[0].x
        self.starting_y = starting_cells[0].y

        # initializes its neighbors as part of the starting empire as well
        # checks to make sure its neighbors are actually close to it
        for neighbor in self.space.get_neighbors(starting_cells[0]):
            if self.space.distance(starting_cells[0], neighbor) < 1:
                starting_cells.append(neighbor)

        # adds the first empire to the empire list
        self.empires.append(Empire(len(self.empires) + 1, self))

        # adds each starting cell to that empire
        for cell in starting_cells:
            cell.religions.clear()
            self.empires[0].add_cell(cell)
            self.default_empire.remove_cell(cell)
            cell.update_religion()
            cell.majReligion = cell.religions[0]
            cell.majReligion.conversion = 1

    # updates the average area of all empires
    def update_avg_area(self):

        # counts only the number of empires with size greater than 5
        # if this is not done, distribution is skewed as small empires pop up on the border of big ones constantly
        count = 0

        # sum of the areas of all empires
        total = 0
        for empire in self.empires:
            if empire.size > 5:
                count += 1
                total += empire.size

        # averages the area of the empires
        if count > 0:
            self.avg_empire_area = total / count

    def tech_drop(self):

        choices = []
        for cell in self.cells:
            if cell.empire.id != 0:
                if len([neighbor for neighbor in cell.neighbors if neighbor.empire.id != cell.empire.id]) == 0:
                    choices.append(cell)
        if len(choices) == 0:
            return
        else:
            cell_choice = random.choice(choices)

        tech_id = len(self.techs_dropped) + 1
        tech_type = random.choice(self.tech_types)
        tech = None
        match tech_type:
            case "Asabiya Growth":
                strength = random.random() * 20
                tech = AsabiyaTechnology(cell_choice, strength, "Growth", tech_id)

            case "Asabiya Decay":
                strength = random.random() * 20
                tech = AsabiyaTechnology(cell_choice, strength, "Decay", tech_id)

            case "Power Decline":
                strength = random.random() * 7
                tech = PowerDeclineTechnology(cell_choice, strength, tech_id)

            case "Delta Power":
                strength = random.random() * 3
                tech = DeltaPowerTechnology(cell_choice, strength, tech_id)

            case "Elevation":
                strength = random.random() * 150
                tech = ElevationTechnology(cell_choice, strength, tech_id)

        cell_choice.add_technology(tech)
        self.techs_dropped.append(tech)

    def update_avg_difference(self):
        if len(self.differences) > 0:
            total = 0
            for diff in self.differences:
                total += abs(diff)
            self.avg_difference = total / len(self.differences)
        self.differences.clear()

    # model actions on each step
    def step(self):

        if self.running:

            # tracks running time
            self.steps += 1

            # updates empires
            # removes them from the empire list if their size is 0 or less
            for empire in self.empires:
                empire.update_size()
                if empire.size == 0:
                    self.empires.remove(empire)
                    continue

                empire.update_properties()

            # updates data variables
            self.update_avg_area()

            # collects data on each step
            self.datacollector.collect(self)

            # steps all cells in a random order
            self.schedule.step()

            # stops the simulation after the inputted number of steps have occurred
            if not self.batch_run and self.steps >= self.sim_length:
                self.running = False

                # determines the quartiles for the heatmap
                percentiles = percentile([cell.times_changed_hands for cell in self.cells], [20, 60, 75, 90])

                # sets the running value for the cells to be false, so they display appropriately
                for cell in self.cells:
                    cell.running = False
                    for perc in percentiles:
                        cell.percentiles.append(perc)
