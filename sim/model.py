
import mesa
import mesa_geo as mg
import random
from mesa import DataCollector
from mesa_geo.raster_layers import Cell, RasterLayer
import seaborn as sns
from matplotlib import pyplot as plot

from cell import EmpireCell
from empire import Empire


# model class
class EuropeModel(mesa.Model):

    def __init__(self, power_decline=4, sim_length=200, delta_power=0.1, asa_growth=0.2, asa_decay=0.1,
                 show_heatmap=False, show_elevation=False, show_coastal=False, show_seaborn_graphs=False):
        super().__init__()

        # power decline is determined by the UI slider
        self.power_decline = power_decline

        # global constants
        # determined by UI slider
        self.delta_power = delta_power
        self.asa_growth = asa_growth
        self.asa_decay = asa_decay

        # sim length is determined by user input
        self.sim_length = sim_length

        # counts steps since the model began running
        self.steps = 0

        # tracks whether the simulation is running
        self.running = True
        self.show_seaborn_graphs = show_seaborn_graphs

        # stores whether the simulation shows the heatmap at the end of its runtime
        self.show_heatmap = show_heatmap

        self.show_elevation = show_elevation
        self.show_coastal = show_coastal

        # sets schedule to be random activation so as not to favor one empire
        self.schedule = mesa.time.RandomActivation(self)

        # list of empires currently in the model
        self.empires = []

        # default empire that all cells start as a part of
        self.default_empire = Empire(0, self)
        self.avg_empire_area = 0

        # area histogram
        # each element is a frequency bar
        self.area_histogram = [0 for x in range(13)]

        # data collector
        # format is {<datapoint name>: lambda model: model.<reporting function or variable>, ...}
        self.datacollector = DataCollector(model_reporters={"starting x": lambda model: model.starting_x,
                                                            "starting y": lambda model: model.starting_y,
                                                            "steps": lambda model: model.steps,
                                                            "Average Empire Area": lambda model: model.avg_empire_area,
                                                            "Number of Empires": lambda model: len([empire for empire in model.empires if empire.size > 5]),
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
                                                            "601 or more Hexes": lambda model: model.area_histogram[12]})

        # creates the geo space with the GeoJSON coordinate system
        self.space = mg.GeoSpace(crs="epsg:4326", warn_crs_conversion=False)

        # adds the elevation raster layer
        # order of precision (ascending):
        # 1. "gis_data/elevation_10.tif"
        # 2. "gis_data/elevation_5.tif"
        # 3. "gis_data/elevation_2-5.tif"
        elevation_layer = RasterLayer.from_file("gis_data/elevation_10.tif", cell_cls=ElevationCell, attr_name="elevation")
        elevation_layer.crs = self.space.crs
        self.space.add_layer(elevation_layer)

        # agent generator
        ac = mg.AgentCreator(EmpireCell, model=self)

        # creates cells from the GeoJSON data file
        self.cells = ac.from_file("gis_data/europe_hex_points.geojson")

        # adds those agents to the geo space
        self.space.add_agents(self.cells)

        # adds all new cells to the default empire
        # also adds them to the scheduler
        for cell in self.cells:
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

        # removes the elevation layer after cell creation to improve performance
        self.space.layers.pop()

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
            self.empires[0].add_cell(cell)
            self.default_empire.remove_cell(cell)

    # updates the average area of all empires
    def update_avg_area(self):

        # counts only the number of empires with size greater than 10
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

    # model actions on each step
    def step(self):

        if self.running:
            # updates empires
            # removes them from the empire list if their size is 0 or less
            for empire in self.empires:
                empire.update_size()
                if empire.size == 0:
                    self.empires.remove(empire)
                    continue

                empire.update_center()
                empire.update_avg_asabiya()

            # updates data variables
            self.update_avg_area()

            # collects data on each step
            self.datacollector.collect(self)

            # steps all cells in a random order
            self.schedule.step()

            # tracks running time
            self.steps += 1

            # stops the simulation after the inputted number of steps have occurred
            if self.steps >= self.sim_length:
                self.running = False

                # determines the quartiles for heatmap data based on
                # the maximum number of times a cell has changed hands
                max_times = max([cell.times_changed_hands for cell in self.cells])
                first_quarter = 0.75 * max_times
                second_quarter = 0.5 * max_times
                third_quarter = 0.25 * max_times

                # sets the running value for the cells to be false, so they display appropriately
                for cell in self.cells:
                    cell.running = False
                    cell.quartiles[0] = first_quarter
                    cell.quartiles[1] = second_quarter
                    cell.quartiles[2] = third_quarter

                if self.show_seaborn_graphs:

                    # list of all empire areas at the end of the simulation
                    area_list = []
                    for empire in self.empires:
                        if empire.size > 5:
                            area_list.append(empire.size)

                    # area distribution histogram
                    max_value = ((max(area_list) // 50) + 1) * 50
                    histogram = sns.histplot(data=area_list, bins=(max_value // 50), binrange=(0, max_value))
                    histogram.set(xlabel="area in hexes", ylabel="frequency")
                    plot.show()

                    # average empire area line graph
                    data = self.datacollector.get_model_vars_dataframe()
                    avg_area = sns.lineplot(data=data, x="steps", y="average empire area")
                    avg_area.set(xlabel="time (steps)")
                    plot.show()

                    # TO DO:
                    # find equivalencies between cells and real world area
                    # area_list = []
                    # for empire in self.empires:
                    #     if empire.size > 5:
                    #         area_list.append(math.log(empire.size))
                    #
                    # max_value = math.ceil(max(area_list))
                    # min_value = math.floor(min(area_list))
                    # histogram = sns.histplot(data=area_list, bins=10, binrange=(min_value, max_value))
                    # histogram.set(xlabel="area in sq km", ylabel="frequency")
                    # plot.show()


# cell to store raster elevation data
# doesn't ever need to change!
class ElevationCell(Cell):
    def __init__(self, pos: mesa.space.Coordinate | None = None, indices: mesa.space.Coordinate | None = None,):
        super().__init__(pos, indices)
        self.elevation = None

    def step(self):
        pass