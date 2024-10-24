import random
from copy import deepcopy
from religion import *


# empire class
# mainly holds cells
class Empire:

    def __init__(self, unique_id, model):

        self.model = model
        self.cells = []
        self.size = 0
        self.center = (None, None)
        self.id = unique_id
        self.average_asabiya = 0
        self.average_us = 0

        if self.id != 0:
            if len(self.model.religions) > 0:
                self.religion = Religion(self.model.religions[len(self.model.religions) - 1].id + 1)
            else:
                self.religion = Religion(1)
            self.model.religions.append(self.religion)
        else:
            self.religion = self.model.default_religion
        self.attack_chance = self.religion.attack_chance

        # gives each empire a random hex code color
        self.color = "#" + str(hex(random.randint(0, 16777216)))[2:]

    # adds a cell to this empire
    def add_cell(self, cell):
        self.cells.append(cell)
        cell.times_changed_hands += 1
        for religion in cell.religions:
            if religion.id == self.id:
                break
        else:
            cell.religions.append(deepcopy(self.religion))
            cell.religions[len(cell.religions) - 1].conversion = 0.25 * cell.religions[0].conversion
            cell.religions[0].conversion *= 0.75

        if cell.ultrasociality > 0 or cell.prev_empire.id == self.id:
            cell.ultrasociality *= -1
        else:
            cell.ultrasociality = 0

        cell.prev_empire = cell.empire
        cell.empire = self
        cell.color = self.color

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

    def update_properties(self):
        # sums the x and y coordinates of all cells in the empire
        x_total = 0
        y_total = 0
        asa_total = 0
        us_total = 0
        for cell in self.cells:
            x_total += cell.x
            y_total += cell.y
            asa_total += cell.asabiya
            us_total += cell.ultrasociality

        self.average_asabiya = asa_total / len(self.cells)
        self.center = round(x_total / len(self.cells)), round(y_total / len(self.cells))
        self.average_us = us_total / len(self.cells)

    # compiled update function
    def update(self):
        self.update_properties()
        self.update_size()
