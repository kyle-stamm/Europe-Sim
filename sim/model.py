import mesa
import random
import math


class Cell(mesa.Agent):

    def __init__(self, unique_id, xcor, ycor, model):
        super().__init__(unique_id, model)

        self.model = model
        self.empire = self.model.default_empire
        self.asabiya = 0.001
        self.power = self.asabiya
        self.elevation = 0
        self.x = xcor
        self.y = ycor
        self.id = unique_id
        self.color = "grey"

    def distance_to_center(self):
        if self.empire.size > 1:
            return math.sqrt((self.empire.center[0] - self.x) ** 2 + (self.empire.center[1] - self.y) ** 2)
        else:
            return 0

    def update_asabiya(self, neighbors):
        for neighbor in neighbors:
            if neighbor.empire.id != self.empire.id:
                border_cell = True
                break
        else:
            border_cell = False

        if border_cell:
            self.asabiya += EuropeModel.asa_growth * self.asabiya * (1 - self.asabiya)
        else:
            self.asabiya -= EuropeModel.asa_decay * self.asabiya

    def attack(self, neighbors):
        attack_choice = random.choice(neighbors)

        if attack_choice.empire.id == self.empire.id:
            for neighbor in neighbors:
                if neighbor.empire.id != self.empire.id:
                    attack_choice = neighbor
                    break
            else:
                return

        if self.power - attack_choice.power > EuropeModel.delta_power:
            attack_choice.empire.remove_cell(attack_choice)
            attack_choice.empire = self.empire
            self.empire.add_cell(attack_choice)
            attack_choice.asabiya = (self.asabiya + attack_choice.asabiya) / 2.0

    def step(self):

        if self.empire.id != 0:

            self.power = self.empire.size * self.empire.average_asabiya * math.exp(-1 * self.distance_to_center() / self.model.power_decline)
            self.color = self.empire.color

            neighbors = self.model.grid.get_neighbors((self.x, self.y), include_center=False, radius=1)
            self.update_asabiya(neighbors)
            self.attack(neighbors)

        else:
            neighbors = self.model.grid.get_neighbors((self.x, self.y), include_center=False, radius=1)

            self.asabiya += EuropeModel.asa_growth * self.asabiya * (1 - self.asabiya)
            self.power = self.asabiya

            if len([neighbor for neighbor in neighbors if neighbor.empire.id != 0]) > 0:
                attack_choice = random.choice([neighbor for neighbor in neighbors if neighbor.empire.id != 0])
            else:
                return

            if self.power - attack_choice.power > EuropeModel.delta_power:
                self.model.empires.append(Empire(len(self.model.empires) + 1, self.model))

                self.model.empires[len(self.model.empires) - 1].add_cell(self)
                self.model.empires[len(self.model.empires) - 1].add_cell(attack_choice)

                self.empire = self.model.empires[len(self.model.empires) - 1]

                attack_choice.empire.remove_cell(attack_choice)
                attack_choice.empire = self.empire
                attack_choice.asabiya = (self.asabiya + attack_choice.asabiya) / 2.0

                self.empire.update()


class Empire:

    colors = ['IndianRed', 'GreenYellow', 'Cornsilk', 'Sienna', 'Maroon',
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
        self.color = Empire.colors[random.randint(0, len(Empire.colors) - 1)]
        self.average_asabiya = 0

    def add_cell(self, cell):
        self.cells.append(cell)
        cell.empire = self

    def remove_cell(self, cell):
        if cell in self.cells:
            self.cells.remove(cell)

    def update_size(self):
        self.size = len(self.cells)

    def update_avg_asabiya(self):

        total = 0
        for cell in self.cells:
            total += cell.asabiya
        self.average_asabiya = total / len(self.cells)

    def update_center(self):

        x_total = 0
        y_total = 0
        for cell in self.cells:
            x_total += cell.x
            y_total += cell.y

        self.center = round(x_total / len(self.cells)), round(y_total / len(self.cells))

    def update(self):
        self.update_avg_asabiya()
        self.update_center()
        self.update_center()


class EuropeModel(mesa.Model):

    delta_power = 0.1
    asa_growth = 0.2
    asa_decay = 0.1

    def __init__(self, num_agents, width, height, power_decline=1.4):
        super().__init__()

        self.power_decline = power_decline
        self.num_agents = num_agents
        self.schedule = mesa.time.RandomActivation(self)
        self.grid = mesa.space.HexSingleGrid(width, height, False)
        self.empires = []
        self.default_empire = Empire(0, self)

        for x in range(self.num_agents):

            cell_x = self.random.randrange(self.grid.width)
            cell_y = self.random.randrange(self.grid.height)
            while not self.grid.is_cell_empty((cell_x, cell_y)):
                cell_x = self.random.randrange(self.grid.width)
                cell_y = self.random.randrange(self.grid.height)

            cell = Cell(x, cell_x, cell_y, self)
            self.schedule.add(cell)
            self.grid.place_agent(cell, (cell_x, cell_y))
            self.default_empire.add_cell(cell)

        starting_x = random.randint(0, self.grid.width)
        starting_y = random.randint(0, self.grid.height)
        for cell in self.grid.coord_iter():
            if cell[1][0] == starting_x and cell[1][1] == starting_y:
                self.empires.append(Empire(len(self.empires) + 1, self))
                self.empires[0].add_cell(cell[0])
                self.default_empire.remove_cell(cell[0])

                initial_neighbors = self.grid.get_neighbors((starting_x, starting_y), include_center=False, radius=1)
                for neighbor in initial_neighbors:
                    self.empires[0].add_cell(neighbor)
                    self.default_empire.remove_cell(neighbor)
                self.empires[0].update()

    def step(self):
        for empire in self.empires:
            empire.update_size()
            if empire.size == 0:
                self.empires.remove(empire)
                continue

            empire.update_center()
            empire.update_avg_asabiya()
        self.schedule.step()


