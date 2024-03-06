
import mesa
import mesa_geo as mg
import random
import math
import shapely
from mesa import DataCollector
from mesa_geo.raster_layers import Cell, RasterLayer


# cell class
# cells are geo agents created from a geojson file
class EmpireCell(mg.GeoAgent):

    # geometry is a shapely object
    # crs will always be epsg:4326 for geojson
    def __init__(self, unique_id, model, geometry, crs):
        super().__init__(unique_id, model, geometry, crs)

        self.geometry = geometry

        # extracts x and y coordinates from the shapely object
        self.x = shapely.get_x(geometry)
        self.y = shapely.get_y(geometry)

        # uses the longitudinal and latitudinal ratio of the cell's position to determine its index in the raster layer
        # has to rounded, so it's not exact, sue me
        self.x_index = round(((180 + self.x) / 360) * self.model.space.layers[0].width)
        self.y_index = round(((90 + self.y) / 180) * self.model.space.layers[0].height)

        # assigns the cell from the raster layer using those indexes
        self.elevation = self.model.space.layers[0][(self.x_index, self.y_index)].elevation
        if self.elevation == -32768:
            self.elevation = 1

        # stores the model that the cells will be loaded into
        self.model = model

        # initializes cells as part of no empire (independent chiefdoms, stored as "default empire")
        self.empire = self.model.default_empire

        # initial asabiya
        self.asabiya = 0.001
        self.power = self.asabiya

        self.id = unique_id

        # initial color for chiefdoms
        self.color = "grey"

        # stores the neighbors of the cell when set up
        self.neighbors = []

    # calculates distance from this cell to the center of the cell's empire
    def distance_to_center(self):

        # checks if the cell is an independent chiefdom or not
        if self.empire.size > 1:

            # if it is not, uses the distance formula between the empire's center and this cell's location
            return math.sqrt((self.empire.center[0] - self.x) ** 2 + (self.empire.center[1] - self.y) ** 2)
        else:

            # if it is, returns 0 as there is only one cell in a chiefdom
            return 0

    # updates the asabiya of the cell
    def update_asabiya(self, neighbors):

        # checks if the cell is a border cell
        # iterates through each neighbor of the cell
        for neighbor in neighbors:

            # if at least one neighbor is found that is an enemy cell
            # flags this cell as a border cell
            if neighbor.empire.id != self.empire.id:
                border_cell = True
                break

        # otherwise, flags this cell as a non-border cell
        else:
            border_cell = False

        # grows or shrinks asabiya according to whether the cell is a border cell
        if border_cell:
            self.asabiya += EuropeModel.asa_growth * self.asabiya * (1 - self.asabiya)
        else:
            self.asabiya -= EuropeModel.asa_decay * self.asabiya

    # allows the cell to attack one of its neighbors
    def attack(self, neighbors):

        # randomly chooses a neighbor to attack
        attack_choice = random.choice(neighbors)

        # determines whether the difference power between the cells is greater than the delta_power value
        if self.power - attack_choice.power > EuropeModel.delta_power:

            # if it is, adds the attacked cell to the attacker's empire

            # removes the attacked cell from its previous empire
            attack_choice.empire.remove_cell(attack_choice)

            # sets the attacked cell's empire to same as the attacker
            attack_choice.empire = self.empire

            # adds the attacked cell to the attacking cell's empire
            self.empire.add_cell(attack_choice)

            # sets the attacked cell's asabiya to be the average of the two cells
            attack_choice.asabiya = (self.asabiya + attack_choice.asabiya) / 2.0

    # sets up the neighbors for each cell
    def setup_neighbors(self):

        # gets the touching neighbors for each cell
        neighbors = self.model.space.get_neighbors(self)

        # checks to make sure that the cells are actually close together on the map
        # cells that are separated by bodies of water are still technically touching,
        # as there are no cells within the body of water
        for neighbor in neighbors:
            if self.model.space.distance(self, neighbor) < 1:
                self.neighbors.append(neighbor)

    # cell actions each step
    def step(self):

        # checks if the cell is an independent chiefdom or part of an empire
        if self.empire.id != 0:

            # if part of an empire

            # sets power according to the Turchin equation
            # power = empire size * average empire asabiya * e^(-1 * distance to empire's center / power decline)
            self.power = self.empire.size * self.empire.average_asabiya * math.exp(-1 * self.distance_to_center() / self.model.power_decline)

            # recolors the empire
            self.color = self.empire.color

            # updates the cell's asabiya
            self.update_asabiya(self.neighbors)

            # attacks if the cell has any neighbors that are enemy cells
            if len([neighbor for neighbor in self.neighbors if neighbor.empire.id != self.empire.id]) > 0:
                self.attack([neighbor for neighbor in self.neighbors if neighbor.empire.id != self.empire.id])

        else:

            # if it is an independent chiefdom

            # it is always a border cell, so asabiya always grows
            self.asabiya += EuropeModel.asa_growth * self.asabiya * (1 - self.asabiya)

            # power is just the asabiya value
            self.power = self.asabiya

            # checks if the cell has neighbors to attack that are part of an empire
            if len([neighbor for neighbor in self.neighbors if neighbor.empire.id != 0]) > 0:
                attack_choice = random.choice([neighbor for neighbor in self.neighbors if neighbor.empire.id != 0])
            else:
                return

            # attacks a neighboring cell with an empire
            if self.power - attack_choice.power > EuropeModel.delta_power:

                # if this cell wins, creates a new empire with this cell and the attacked cell
                self.model.empires.append(Empire(len(self.model.empires) + 1, self.model))

                # adds both cells to the new empire
                self.model.empires[len(self.model.empires) - 1].add_cell(self)
                self.model.empires[len(self.model.empires) - 1].add_cell(attack_choice)

                self.empire = self.model.empires[len(self.model.empires) - 1]

                # removes the attacked cell from its previous empire
                attack_choice.empire.remove_cell(attack_choice)
                attack_choice.empire = self.empire
                attack_choice.asabiya = (self.asabiya + attack_choice.asabiya) / 2.0

                # updates the new empire
                self.empire.update()


# empire class
# mainly holds cells
class Empire:

    # HTML colors
    # will add more when I'm not being lazy
    colors = ['IndianRed', 'GreenYellow', 'Sienna', 'Maroon',
              'DeepPink', 'DarkGreen', 'MediumAquamarine', 'Orange', 'Gold',
              "Red", "Cyan", "Blue", "DarkBlue", "LightBlue", "Purple",
              "Yellow", "Lime", "Magenta", "Pink", "Brown", "Olive",
              "Aquamarine"]

    def __init__(self, unique_id, model):

        self.model = model
        self.cells = []
        self.size = 0
        self.center = (None, None)
        self.id = unique_id

        # picks a random color from the color list
        self.color = Empire.colors[random.randint(0, len(Empire.colors) - 1)]
        self.average_asabiya = 0

    # adds a cell to this empire
    def add_cell(self, cell):
        self.cells.append(cell)
        cell.empire = self

    # removes a cell from this empire
    def remove_cell(self, cell):
        if cell in self.cells:
            self.cells.remove(cell)

    # updates size according to the number of cells held
    # also updates the area histogram accordingly
    def update_size(self):

        if self.size > 5:
            if self.size > 600:
                self.model.area_histogram[12] -= 1
            else:
                self.model.area_histogram[self.size // 50] -= 1

        self.size = len(self.cells)
        if self.size > 5:
            if self.size > 600:
                self.model.area_histogram[12] += 1
            else:
                self.model.area_histogram[self.size // 50] += 1

    # updates the average asabiya
    def update_avg_asabiya(self):

        # sums the asabiyas of all cells in the empire
        total = 0
        for cell in self.cells:
            total += cell.asabiya

        # divides by the number of cells in the empire
        self.average_asabiya = total / len(self.cells)

    # updates the center point of the empire
    def update_center(self):

        # sums the x and y coordinates of all cells in the empire
        x_total = 0
        y_total = 0
        for cell in self.cells:
            x_total += cell.x
            y_total += cell.y

        # divides those totals by the number of cells
        self.center = round(x_total / len(self.cells)), round(y_total / len(self.cells))

    # compiled update function
    def update(self):
        self.update_avg_asabiya()
        self.update_center()


# cell to store raster elevation data
# doesn't ever need to change!
class ElevationCell(Cell):
    def __init__(self, pos: mesa.space.Coordinate | None = None, indices: mesa.space.Coordinate | None = None,):
        super().__init__(pos, indices)
        self.elevation = None

    def step(self):
        pass


# model class
class EuropeModel(mesa.Model):

    # global constants
    delta_power = 0.1
    asa_growth = 0.2
    asa_decay = 0.1

    def __init__(self, power_decline=1.4):
        super().__init__()

        # power decline is determined by the UI slider
        self.power_decline = power_decline

        # counts steps since the model began running
        self.steps = 0

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
        # format is {<datapoint name>: lambda model: model.<reporting function or variable>}
        self.datacollector = DataCollector(model_reporters={"average empire area": lambda model: model.avg_empire_area,
                                                            "number of empires with more than 5 hexes": lambda model: len([empire for empire in model.empires if empire.size > 5]),
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

        # removes the elevation layer after cell creation to improve performance
        self.space.layers.pop()

        # sets up the initial empire

        # picks a random cell
        starting_cells = [self.cells[random.randint(0, len(self.cells) - 1)]]

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

    # model actions on each step
    def step(self):

        # updates empires
        # removes them from the empire list if their size is 0 or less
        for empire in self.empires:
            empire.update_size()
            if empire.size <= 0:
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
