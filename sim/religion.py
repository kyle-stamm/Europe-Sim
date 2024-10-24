import random

class Religion:

    types = ["pros", "non-pros"]
    def __init__(self, id):
        self.id = id
        self.type = random.choice(self.types)
        self.tolerance = random.random() + 0.5
        self.conversion = 0

        if self.type == "pros":
            self.attack_chance = 0.65 * (2 - self.tolerance)
            self.conv_chance = 0.3
        elif self.type == "non-pros":
            self.attack_chance = 0.35 * (2 - self.tolerance)
            self.conv_chance = 0.15

