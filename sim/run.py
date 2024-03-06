import seaborn as sns
import numpy
import pandas
from matplotlib import pyplot as plot

from model import EuropeModel

model = EuropeModel(power_decline=1.4)
for x in range(200):
    model.step()

