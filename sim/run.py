import seaborn as sns
import numpy
import pandas
from matplotlib import pyplot as plot

from model import EuropeModel

model = EuropeModel(power_decline=1.4)
for x in range(1):
    model.step()

# avg_area = model.avg_area_data.get_model_vars_dataframe()
# line_plot = sns.lineplot(data=avg_area)
# line_plot.set(title="average empire area over time", ylabel="avg area")
# plot.show()

# area_hist = model.area_histogram
# histogram = sns.histplot(data=area_hist, binwidth=50)
# histogram.set(title="empire area distribution", xlabel="area in hexes", ylabel="frequency")
# plot.show()
