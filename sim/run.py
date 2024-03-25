
import mesa
import pandas
import seaborn as sns
from matplotlib import pyplot as plot

from model import EuropeModel

# parameters to run the batch run tests over
# format is {"<parameter name>": <single value of list of values>, ...}
power_decline_test_parameters = {"power_decline": [x / 10.0 for x in range(1, 81)]}
starting_point_test_parameters = {"power_decline": 4.0}
delta_power_test_parameters = {"delta_power": [x / 100.0 for x in range(1, 21)]}
asa_growth_test_parameters = {"asa_growth": [x / 100.0 for x in range(1, 31)]}
asa_decay_test_parameters = {"asa_decay": [x / 100.0 for x in range(1, 31)]}
elevation_test_parameters = {"use_elevation": [True, False], "power_decline": [x / 10.0 for x in range(1, 81)]}
heatmap_test_parameters = {"power_decline": 4}

# columns to include in the spreadsheet output
# have to have the same names as the reporters in the model's datacollector
default_columns = ['Average Empire Area', 'Number of Empires', "5-50 Hexes",
                   "51-100 Hexes", "101-150 Hexes", "151-200 Hexes", "201-250 Hexes",
                   "251-300 Hexes", "301-350 Hexes", "351-400 Hexes", "401-450 Hexes",
                   "451-500 Hexes", "501-550 Hexes", "551-600 Hexes", "601 or more Hexes"]
power_decline_columns = ['power_decline']
starting_point_columns = ['starting x', 'starting y']
delta_power_columns = ['delta_power']
asa_growth_columns = ['asa_growth']
asa_decay_columns = ['asa_decay']
elevation_columns = ['use_elevation', 'power_decline']


if __name__ == '__main__':

    prompt_text = ("1. Model Modification Test\n"
                   "2. Power Decline Tests\n"
                   "3. Starting Position Tests\n"
                   "4. Delta Power Tests\n"
                   "5. Asabiya Growth Tests\n"
                   "6. Asabiya Decay Tests\n"
                   "7. Elevation Tests\n"
                   "8. Times Changed Hands Tests\n")
    test = input(prompt_text)

    if test == "1":
        ticks = 1
        model = EuropeModel(power_decline=1.4, sim_length=ticks)
        for x in range(ticks):
            model.step()
    elif test == "2":
        data = mesa.batch_run(model_cls=EuropeModel, parameters=power_decline_test_parameters, number_processes=8, max_steps=400, iterations=1)

        power_decline_dataframe = pandas.DataFrame(data=data, columns=(power_decline_columns + default_columns))
        power_decline_dataframe.to_csv(path_or_buf='output_data/power_decline.csv', index_label="trial")

        pd_vs_area = sns.scatterplot(data=power_decline_dataframe, x="power_decline", y="Average Empire Area")
        pd_vs_area.set(xlabel="Power Decline", ylabel="Average Empire Area")
        plot.show()

        pd_vs_num_empires = sns.scatterplot(data=power_decline_dataframe, x="power_decline", y="Number of Empires")
        pd_vs_num_empires.set(xlabel="Power Decline", ylabel="Number of Empires")
        plot.show()

    elif test == "3":
        data = mesa.batch_run(model_cls=EuropeModel, parameters=starting_point_test_parameters, number_processes=8, max_steps=400, iterations=240)

        starting_point_dataframe = pandas.DataFrame(data=data, columns=(starting_point_columns + default_columns))
        starting_point_dataframe.to_csv(path_or_buf="output_data/starting_point.csv", index_label="trial")

        spx_vs_area = sns.scatterplot(data=starting_point_dataframe, x="starting x", y="Average Empire Area")
        spx_vs_area.set(xlabel="Starting X Coordinate", ylabel="Average Empire Area")
        plot.show()

        spy_vs_area = sns.scatterplot(data=starting_point_dataframe, x="starting y", y="Average Empire Area")
        spy_vs_area.set(xlabel="Starting Y Coordinate", ylabel="Average Empire Area")
        plot.show()
    elif test == "4":
        data = mesa.batch_run(model_cls=EuropeModel, parameters=delta_power_test_parameters, number_processes=8, max_steps=400, iterations=3)

        delta_power_dataframe = pandas.DataFrame(data=data, columns=(delta_power_columns + default_columns))
        delta_power_dataframe.to_csv(path_or_buf="output_data/delta_power.csv", index_label="trial")

        dp_vs_area = sns.scatterplot(data=delta_power_dataframe, x="delta_power", y="Average Empire Area")
        dp_vs_area.set(xlabel="Delta Power", ylabel="Average Empire Area")
        plot.show()

        dp_vs_num_empires = sns.scatterplot(data=delta_power_dataframe, x="delta_power", y="Number of Empires")
        dp_vs_num_empires.set(xlabel="Delta Power", ylabel="Number of Empires")
        plot.show()
    elif test == "5":
        data = mesa.batch_run(model_cls=EuropeModel, parameters=asa_growth_test_parameters, number_processes=8, max_steps=400, iterations=3)

        delta_power_dataframe = pandas.DataFrame(data=data, columns=(asa_growth_columns + default_columns))
        delta_power_dataframe.to_csv(path_or_buf="output_data/asa_growth.csv", index_label="trial")

        ag_vs_area = sns.scatterplot(data=delta_power_dataframe, x="asa_growth", y="Average Empire Area")
        ag_vs_area.set(xlabel="Asabiya Growth", ylabel="Average Empire Area")
        plot.show()

        ag_vs_num_empires = sns.scatterplot(data=delta_power_dataframe, x="asa_growth", y="Number of Empires")
        ag_vs_num_empires.set(xlabel="Asabiya Growth", ylabel="Number of Empires")
        plot.show()
    elif test == "6":
        data = mesa.batch_run(model_cls=EuropeModel, parameters=asa_decay_test_parameters, number_processes=8, max_steps=400, iterations=3)

        delta_power_dataframe = pandas.DataFrame(data=data, columns=(asa_decay_columns + default_columns))
        delta_power_dataframe.to_csv(path_or_buf="output_data/asa_decay.csv", index_label="trial")

        ad_vs_area = sns.scatterplot(data=delta_power_dataframe, x="asa_decay", y="Average Empire Area")
        ad_vs_area.set(xlabel="Asabiya Decay", ylabel="Average Empire Area")
        plot.show()

        ad_vs_num_empires = sns.scatterplot(data=delta_power_dataframe, x="asa_decay", y="Number of Empires")
        ad_vs_num_empires.set(xlabel="Asabiya Decay", ylabel="Number of Empires")
        plot.show()
    elif test == "7":
        data = mesa.batch_run(model_cls=EuropeModel, parameters=elevation_test_parameters, number_processes=8, max_steps=400, iterations=1)

        delta_power_dataframe = pandas.DataFrame(data=data, columns=(elevation_columns + default_columns))
        delta_power_dataframe.to_csv(path_or_buf="output_data/use_elevation.csv", index_label="trial")
    elif test == "8":
        data = mesa.batch_run(model_cls=EuropeModel, parameters=heatmap_test_parameters, number_processes=8, max_steps=400, iterations=1)

        heatmap_dataframe = pandas.DataFrame(data=data, columns=["Elevation", "Times Changed Hands"])
        heatmap_dataframe.to_csv(path_or_buf="output_data/heatmap.csv", index_label="cell")

        elev_vs_times = sns.scatterplot(data=heatmap_dataframe, x="Elevation", y="Times Changed Hands")
        elev_vs_times.set(xlabel="Elevation", ylabel="Times Changed Hands")
        plot.show()
