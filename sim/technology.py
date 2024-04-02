
class Technology:

    def __init__(self, cell, tech_id):
        self.cell = cell
        self.tech_id = tech_id


class AsabiyaTechnology(Technology):

    def __init__(self, cell, value, type, tech_id):
        super().__init__(cell, tech_id)
        self.value = value
        self.type = type
        self.name = "Asabiya " + type

    def use(self):
        if self.type == "Decay":
            if (self.cell.asa_decay - self.value) >= 0.01:
                self.cell.asa_decay -= self.value
                self.cell.asa_decay_bonus += self.value
        else:
            self.cell.asa_growth += self.value
            self.cell.asa_growth_bonus += self.value


class ElevationTechnology(Technology):

    def __init__(self, cell, value, tech_id):
        super().__init__(cell, tech_id)
        self.value = value
        self.name = "Elevation"

    def use(self):
        self.cell.elevation_bonus += self.value


class PowerDeclineTechnology(Technology):
    def __init__(self, cell, value, tech_id):
        super().__init__(cell, tech_id)
        self.value = value
        self.name = "Power Decline"

    def use(self):
        self.cell.power_decline_bonus += self.value
        self.cell.power_decline += self.value


class DeltaPowerTechnology(Technology):

    def __init__(self, cell, value, tech_id):
        super().__init__(cell, tech_id)
        self.value = value
        self.name = "Delta Power"

    def use(self):
        if (self.cell.delta_power_bonus - self.value) >= 0.01:
            self.cell.delta_power_bonus += self.value
            self.cell.delta_power -= self.value

