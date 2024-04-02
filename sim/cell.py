import mesa_geo as mg
import random
import math
import shapely

from empire import Empire


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
        total_bounds = self.model.space.total_bounds
        if self.x > 0:
            self.x_index = round(((self.x + abs(total_bounds[0])) / (total_bounds[2] - total_bounds[0])) * self.model.space.layers[0].width)
        else:
            self.x_index = round((abs(total_bounds[0]) + self.x) / (total_bounds[2] - total_bounds[0]) * self.model.space.layers[0].width)
        self.y_index = round(((self.y - total_bounds[1]) / (total_bounds[3] - total_bounds[1])) * self.model.space.layers[0].height)

        # index clamping to prevent index errors caused by rounding
        if self.x_index > self.model.space.layers[0].width - 1:
            self.x_index = self.model.space.layers[0].width - 1
        elif self.x_index < 0:
            self.x_index = 0

        if self.y_index > self.model.space.layers[0].height - 1:
            self.y_index = self.model.space.layers[0].height - 1
        elif self.y_index < 0:
            self.y_index = 0

        # assigns the cell from the raster layer using those indexes
        self.elevation = self.model.space.layers[0][(self.x_index, self.y_index)].elevation
        if self.elevation == -32768:
            self.elevation = 1

        self.power_decline_bonus = 0
        self.delta_power_bonus = 0
        self.elevation_bonus = 1
        self.asa_growth_bonus = 0
        self.asa_decay_bonus = 0

        # whether the cell is coastal or not
        self.coastal = False

        # whether the model is running or not
        # used for showing the heatmap
        self.running = True

        # whether to show the heatmap at the end or not
        self.show_heatmap = False

        self.show_elevation = False
        self.show_coastal = False

        # determines which quartile of the heatmap data the cell falls into
        self.percentiles = []

        # counts how many times the cell has changed hands between empires
        self.times_changed_hands = -1

        # stores the model that the cells will be loaded into
        self.model = model

        # initializes cells as part of no empire (independent chiefdoms, stored as "default empire")
        self.empire = self.model.default_empire

        # initial asabiya
        self.asabiya = 0.001
        self.power = self.asabiya
        self.asa_growth = self.model.asa_growth
        self.asa_decay = self.model.asa_decay

        self.power_decline = self.model.power_decline
        self.delta_power = self.model.delta_power

        self.technology = []

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
            self.asabiya += self.asa_growth * self.asabiya * (1 - self.asabiya)
        else:
            self.asabiya -= self.asa_decay * self.asabiya

    # allows the cell to attack one of its neighbors
    def attack(self, neighbors):

        # randomly chooses a neighbor to attack
        attack_choice = random.choice(neighbors)

        if self.model.use_elevation:
            # calculation of the attacked cell's elevation modifier
            # easier to win if the attacked cell is at a lower elevation
            # harder to win if the attacked cell is at a higher elevation
            if (self.elevation - attack_choice.elevation) > 0:
                elevation_modifier = (self.model.elevation_constant - math.log(self.elevation - attack_choice.elevation)) / self.model.elevation_constant
                if elevation_modifier <= 0:
                    elevation_modifier = 0.01
            elif (self.elevation - attack_choice.elevation) < 0:
                elevation_modifier = (self.model.elevation_constant + math.log(abs(self.elevation - attack_choice.elevation))) / self.model.elevation_constant
            else:
                elevation_modifier = 1
        else:
            elevation_modifier = 1
        elevation_modifier /= self.elevation_bonus

        # determines whether the difference power between the cells is greater than the delta_power value
        if self.power - (attack_choice.power * elevation_modifier) > self.delta_power:

            # if it is, adds the attacked cell to the attacker's empire

            # removes the attacked cell from its previous empire
            attack_choice.empire.remove_cell(attack_choice)

            # sets the attacked cell's empire to same as the attacker
            attack_choice.empire = self.empire

            # adds the attacked cell to the attacking cell's empire
            self.empire.add_cell(attack_choice)

            # sets the attacked cell's asabiya to be the average of the two cells
            attack_choice.asabiya = (self.asabiya + attack_choice.asabiya) / 2.0
            attack_choice.clear_technology()

            for tech in self.technology:
                attack_choice.add_technology(tech)

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

        if len(self.neighbors) < 6 and (self.x - 1) > -12 and (self.x + 1) < 48 and (self.y - 1) > 26 and (self.y + 1) < 62.75:
            self.coastal = True

    def fix_coastal(self):

        # fixes the bottom left corner of morocco
        if self.y < 29.5 and self.x < 10:
            self.coastal = False

        # fixes the cells in the middle of Europe
        for neighbor in self.neighbors:
            if neighbor.coastal:
                return
        else:
            self.coastal = False

    def add_technology(self, tech):
        self.technology.append(tech)
        self.technology[len(self.technology) - 1].use()

    def clear_technology(self):
        self.technology.clear()

        self.power_decline = self.model.power_decline
        self.power_decline_bonus = 0

        self.asa_growth = self.model.asa_growth
        self.asa_growth_bonus = 0

        self.asa_decay = self.model.asa_decay
        self.asa_decay_bonus = 0

        self.delta_power_bonus = self.model.delta_power
        self.delta_power_bonus = 0

        self.elevation_bonus = 1

    def spread_technology(self):

        spread_choice = random.choice(self.neighbors)
        tech_choice = random.choice(self.technology)
        if spread_choice.empire.id == 0:
            return

        for tech in spread_choice.technology:
            if tech.tech_id == tech_choice.tech_id:
                return
        else:
            if self.empire.id == spread_choice.empire.id:
                chance = 80
            else:
                return

            if self.model.use_elevation:
                # calculation of the attacked cell's elevation modifier
                # easier to win if the attacked cell is at a lower elevation
                # harder to win if the attacked cell is at a higher elevation
                if (self.elevation - spread_choice.elevation) > 0:
                    elevation_modifier = (self.model.elevation_constant - math.log(self.elevation - spread_choice.elevation)) / self.model.elevation_constant
                    if elevation_modifier <= 0:
                        elevation_modifier = 0.01
                elif (self.elevation - spread_choice.elevation) < 0:
                    elevation_modifier = (self.model.elevation_constant + math.log(abs(self.elevation - spread_choice.elevation))) / self.model.elevation_constant
                else:
                    elevation_modifier = 1
            else:
                elevation_modifier = 1
            chance /= elevation_modifier

            if (random.random() * 100) <= chance:
                spread_choice.add_technology(tech_choice)


    # cell actions each step
    def step(self):

        # checks if the cell is an independent chiefdom or part of an empire
        if self.empire.id != 0:

            # if part of an empire

            # sets power according to the Turchin equation
            # power = empire size * average empire asabiya * e^(-1 * distance to empire's center / power decline)
            self.power = self.empire.size * self.empire.average_asabiya * math.exp(-1 * self.distance_to_center() / self.power_decline)

            # recolors the empire
            self.color = self.empire.color

            # updates the cell's asabiya
            self.update_asabiya(self.neighbors)

            # attacks if the cell has any neighbors that are enemy cells
            if len([neighbor for neighbor in self.neighbors if neighbor.empire.id != self.empire.id]) > 0:
                self.attack([neighbor for neighbor in self.neighbors if neighbor.empire.id != self.empire.id])
            if len(self.technology) > 0:
                self.spread_technology()

        else:

            # if it is an independent chiefdom

            # it is always a border cell, so asabiya always grows
            self.asabiya += self.model.asa_growth * self.asabiya * (1 - self.asabiya)

            # power is just the asabiya value
            self.power = self.asabiya

            # checks if the cell has neighbors to attack that are part of an empire
            if len([neighbor for neighbor in self.neighbors if neighbor.empire.id != 0]) > 0:
                attack_choice = random.choice([neighbor for neighbor in self.neighbors if neighbor.empire.id != 0])
            else:
                return

            if self.model.use_elevation:
                # calculation of the attacked cell's elevation modifier
                # easier to win if the attacked cell is at a lower elevation
                # harder to win if the attacked cell is at a higher elevation
                if (self.elevation - attack_choice.elevation) > 0:
                    elevation_modifier = (self.model.elevation_constant - math.log(self.elevation - attack_choice.elevation)) / self.model.elevation_constant
                    if elevation_modifier <= 0:
                        elevation_modifier = 0.01
                elif (self.elevation - attack_choice.elevation) < 0:
                    elevation_modifier = (self.model.elevation_constant + math.log(abs(self.elevation - attack_choice.elevation))) / self.model.elevation_constant
                else:
                    elevation_modifier = 1
            else:
                elevation_modifier = 1

            # attacks a neighboring cell with an empire
            if self.power - (attack_choice.power * elevation_modifier) > self.model.delta_power:

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
                attack_choice.clear_technology()

                # updates the new empire
                self.empire.update()