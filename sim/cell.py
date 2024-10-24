import mesa_geo as mg
import random
import math
import shapely

from empire import Empire
from religion import *

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

        self.elevation = None

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
        self.prev_empire = None

        # initial asabiya
        self.asabiya = 0.001
        self.power = 0

        self.fortification = 1

        self.ultrasociality = 5

        self.majReligion = Religion(0)
        self.majReligion.type = "non-pros"
        self.majReligion.tolerance = 0.75
        self.majReligion.conversion = 1
        self.religions = [self.majReligion]

        self.id = unique_id

        # initial color for chiefdoms
        self.color = "grey"

        # stores the neighbors of the cell when set up
        self.neighbors = []

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
                chance = 5

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

    # updates the asabiya of the cell
    def update_asabiya(self):

        if self.empire.id != 0:
            # checks if the cell is a border cell
            # iterates through each neighbor of the cell
            for neighbor in self.neighbors:

                # if at least one neighbor is found that is an enemy cell
                # flags this cell as a border cell
                if neighbor.empire.id != self.empire.id:
                    border_cell = True
                    break

            # otherwise, flags this cell as a non-border cell
            else:
                border_cell = False
        else:
            border_cell = True

        # grows or shrinks asabiya according to whether the cell is a border cell
        if border_cell:
            self.asabiya += self.model.asa_growth * self.asabiya * (1 - self.asabiya)
        else:
            self.asabiya -= self.model.asa_decay * self.asabiya

    def update_religion(self):

        for religion in self.religions:
            if religion.id != 0:
                chance = religion.conv_chance * religion.conversion

                for neighbor in self.neighbors:
                    if neighbor.majReligion and (neighbor.majReligion.id == religion.id and neighbor.majReligion.id != 0):
                        chance += 0.025

                if self.majReligion and religion != self.majReligion:
                    tolerance_mod = self.majReligion.tolerance
                else:
                    tolerance_mod = 1

                if self.majReligion and self.majReligion.type == "non-pros":
                    pros_mod = (1 - self.majReligion.conversion) / 2
                else:
                    pros_mod = 1

                if self.elevation > 0:
                    elev_mod = math.log(self.elevation, 10)
                    if elev_mod > 1:
                        elev_mod = 1 / elev_mod
                else:
                    elev_mod = 1

                if random.random() < chance * tolerance_mod * pros_mod * elev_mod:
                    if religion.id == self.empire.religion.id:
                        conv_increase = 0.1
                    else:
                        conv_increase = 0.025
                    religion.conversion += conv_increase
                    for r in self.religions:
                        if r.id != religion.id:
                            r.conversion -= round(conv_increase / (len(self.religions) - 1), 3)

        for religion in self.religions:
            if religion.conversion < 0:
                self.religions.remove(religion)
            elif religion.conversion > 1:
                religion.conversion = 1

        self.religions.sort(reverse=True, key=lambda rel: rel.conversion)
        self.majReligion = self.religions[0]

        if self.majReligion.conversion < 0.5:
            self.majReligion = None

    def update_ultrasociality(self):
        self.ultrasociality += 0.25
        if self.ultrasociality > 5:
            self.ultrasociality = 5

    def update_power(self):
        if self.majReligion == self.empire.religion:
            relMatchBonus = 1.2
        else:
            relMatchBonus = 1

        # sets power according to the Turchin equation
        # power = empire size * average empire asabiya * e^(-1 * distance to empire's center / power decline)
        if self.empire.id != 0:
            self.power = self.empire.size * (5 * relMatchBonus + self.ultrasociality) * self.empire.average_asabiya * math.exp(-1 * self.distance_to_center() / self.model.power_decline)
        else:
            self.power = self.asabiya * (5 - self.ultrasociality)

    def elevation_modifier(self, attack_choice):
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

        return elevation_modifier

        # allows the cell to attack one of its neighbors

    # calculates distance from this cell to the center of the cell's empire
    def distance_to_center(self):

        # checks if the cell is an independent chiefdom or not
        if self.empire.size > 1:

            # if it is not, uses the distance formula between the empire's center and this cell's location
            return math.sqrt((self.empire.center[0] - self.x) ** 2 + (self.empire.center[1] - self.y) ** 2)
        else:

            # if it is, returns 0 as there is only one cell in a chiefdom
            return 0

    def attack(self, enemy_neighbors):

        # randomly chooses a neighbor to attack
        attack_choice = random.choice(enemy_neighbors)

        # self.model.differences.append(round(self.power - (attack_choice.power * elevation_modifier), 2))

        print(f"Difference: {self.power - (attack_choice.power * self.elevation_modifier(attack_choice) * attack_choice.fortification)}")
        # determines whether the difference power between the cells is greater than the delta_power value
        if self.power - (attack_choice.power * self.elevation_modifier(attack_choice) * attack_choice.fortification) > self.model.delta_power:
            if self.empire.id != 0:
                # if it is, adds the attacked cell to the attacker's empire

                # removes the attacked cell from its previous empire
                attack_choice.empire.remove_cell(attack_choice)

                # adds the attacked cell to the attacking cell's empire
                self.empire.add_cell(attack_choice)

                # sets the attacked cell's asabiya to be the average of the two cells
                attack_choice.asabiya = (self.asabiya + attack_choice.asabiya) / 2.0
            else:
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

    # cell actions each step
    def step(self):

        choices = [neighbor for neighbor in self.neighbors if neighbor.empire.id != self.empire.id]
        self.update_religion()
        self.update_ultrasociality()
        self.update_asabiya()
        self.update_power()

        # attacks if the cell has any neighbors that are enemy cells
        if len(choices) > 0:
            if self.empire.id != 0:
                if random.random() < self.empire.attack_chance:
                    self.attack(choices)
                    self.fortification = 1
                else:
                    if self.fortification < 2:
                        self.fortification += 0.2
            else:
                self.attack(choices)
