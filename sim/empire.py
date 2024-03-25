import random


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

        # gives each empire a random hex code color
        self.color = "#" + str(hex(random.randint(0, 16777216)))[2:]

    # adds a cell to this empire
    def add_cell(self, cell):
        self.cells.append(cell)
        cell.empire = self
        cell.times_changed_hands += 1

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