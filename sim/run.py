from model import EuropeModel

ticks = 100
model = EuropeModel(power_decline=1.4, sim_length=ticks)
for x in range(ticks):
    model.step()

