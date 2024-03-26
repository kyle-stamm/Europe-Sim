
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
use_elevation_test_parameters = {"use_elevation": [True, False], "power_decline": [x / 10.0 for x in range(1, 81)]}
heatmap_test_parameters = {"power_decline": 4}
elevation_constant_test_parameters = {"elevation_constant": [x for x in range(0, 10)]}

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
use_elevation_columns = ['use_elevation', 'power_decline']
elevation_constant_columns = ['elevation_constant']


if __name__ == '__main__':

    prompt_text = ("1. Model Modification Test\n"
                   "2. Power Decline Tests\n"
                   "3. Starting Position Tests\n"
                   "4. Delta Power Tests\n"
                   "5. Asabiya Growth Tests\n"
                   "6. Asabiya Decay Tests\n"
                   "7. Use Elevation Tests\n"
                   "8. Times Changed Hands Tests\n"
                   "9. Elevation Constant Tests\n")
    test = input(prompt_text)

    match test:
        case "1":
            ticks = 1
            model = EuropeModel(power_decline=1.4, sim_length=ticks)
            for x in range(ticks):
                model.step()
        case "2":
            data = mesa.batch_run(model_cls=EuropeModel, parameters=power_decline_test_parameters, number_processes=8, max_steps=400, iterations=1)

            power_decline_dataframe = pandas.DataFrame(data=data, columns=(power_decline_columns + default_columns))
            power_decline_dataframe.to_csv(path_or_buf='output_data/power_decline.csv', index_label="trial")

            pd_vs_area = sns.scatterplot(data=power_decline_dataframe, x="power_decline", y="Average Empire Area")
            pd_vs_area.set(xlabel="Power Decline", ylabel="Average Empire Area")
            plot.show()

            pd_vs_num_empires = sns.scatterplot(data=power_decline_dataframe, x="power_decline", y="Number of Empires")
            pd_vs_num_empires.set(xlabel="Power Decline", ylabel="Number of Empires")
            plot.show()

        case "3":
            data = mesa.batch_run(model_cls=EuropeModel, parameters=starting_point_test_parameters, number_processes=8, max_steps=400, iterations=250)

            starting_point_dataframe = pandas.DataFrame(data=data, columns=(starting_point_columns + default_columns))
            starting_point_dataframe.to_csv(path_or_buf="output_data/starting_point.csv", index_label="trial")

            spx_vs_area = sns.scatterplot(data=starting_point_dataframe, x="starting x", y="Average Empire Area")
            spx_vs_area.set(xlabel="Starting X Coordinate", ylabel="Average Empire Area")
            plot.show()

            spy_vs_area = sns.scatterplot(data=starting_point_dataframe, x="starting y", y="Average Empire Area")
            spy_vs_area.set(xlabel="Starting Y Coordinate", ylabel="Average Empire Area")
            plot.show()
        case "4":
            data = mesa.batch_run(model_cls=EuropeModel, parameters=delta_power_test_parameters, number_processes=8, max_steps=400, iterations=3)

            delta_power_dataframe = pandas.DataFrame(data=data, columns=(delta_power_columns + default_columns))
            delta_power_dataframe.to_csv(path_or_buf="output_data/delta_power.csv", index_label="trial")

            dp_vs_area = sns.scatterplot(data=delta_power_dataframe, x="delta_power", y="Average Empire Area")
            dp_vs_area.set(xlabel="Delta Power", ylabel="Average Empire Area")
            plot.show()

            dp_vs_num_empires = sns.scatterplot(data=delta_power_dataframe, x="delta_power", y="Number of Empires")
            dp_vs_num_empires.set(xlabel="Delta Power", ylabel="Number of Empires")
            plot.show()
        case "5":
            data = mesa.batch_run(model_cls=EuropeModel, parameters=asa_growth_test_parameters, number_processes=8, max_steps=400, iterations=3)

            delta_power_dataframe = pandas.DataFrame(data=data, columns=(asa_growth_columns + default_columns))
            delta_power_dataframe.to_csv(path_or_buf="output_data/asa_growth.csv", index_label="trial")

            ag_vs_area = sns.scatterplot(data=delta_power_dataframe, x="asa_growth", y="Average Empire Area")
            ag_vs_area.set(xlabel="Asabiya Growth", ylabel="Average Empire Area")
            plot.show()

            ag_vs_num_empires = sns.scatterplot(data=delta_power_dataframe, x="asa_growth", y="Number of Empires")
            ag_vs_num_empires.set(xlabel="Asabiya Growth", ylabel="Number of Empires")
            plot.show()
        case "6":
            data = mesa.batch_run(model_cls=EuropeModel, parameters=asa_decay_test_parameters, number_processes=8, max_steps=400, iterations=3)

            delta_power_dataframe = pandas.DataFrame(data=data, columns=(asa_decay_columns + default_columns))
            delta_power_dataframe.to_csv(path_or_buf="output_data/asa_decay.csv", index_label="trial")

            ad_vs_area = sns.scatterplot(data=delta_power_dataframe, x="asa_decay", y="Average Empire Area")
            ad_vs_area.set(xlabel="Asabiya Decay", ylabel="Average Empire Area")
            plot.show()

            ad_vs_num_empires = sns.scatterplot(data=delta_power_dataframe, x="asa_decay", y="Number of Empires")
            ad_vs_num_empires.set(xlabel="Asabiya Decay", ylabel="Number of Empires")
            plot.show()
        case "7":
            data = mesa.batch_run(model_cls=EuropeModel, parameters=use_elevation_test_parameters, number_processes=8, max_steps=400, iterations=1)

            delta_power_dataframe = pandas.DataFrame(data=data, columns=(use_elevation_columns + default_columns))
            delta_power_dataframe.to_csv(path_or_buf="output_data/use_elevation.csv", index_label="trial")
        case "8":
            ticks = 400
            model = EuropeModel(power_decline=8, sim_length=ticks)
            for x in range(ticks):
                model.step()

            elevations = []
            times_changed_hands = []
            for cell in model.cells:
                elevations.append(cell.elevation)
                times_changed_hands.append(cell.times_changed_hands)

            data = {"Elevation": elevations, "Times Changed Hands": times_changed_hands}

            heatmap_dataframe = pandas.DataFrame(data)
            heatmap_dataframe.to_csv(path_or_buf="output_data/heatmap.csv", index_label="Cell")

            elev_vs_times = sns.scatterplot(data=heatmap_dataframe, x="Elevation", y="Times Changed Hands")
            elev_vs_times.set(xlabel="Elevation", ylabel="Times Changed Hands")
            plot.show()
        case "9":
            data = mesa.batch_run(model_cls=EuropeModel, parameters=elevation_constant_test_parameters, number_processes=8, max_steps=400, iterations=8)

            elevation_constant_dataframe = pandas.DataFrame(data=data, columns=(elevation_constant_columns + default_columns))
            elevation_constant_dataframe.to_csv(path_or_buf="output_data/elevation_constant.csv", index_label="trial")

            elev_const_vs_area = sns.scatterplot(data=elevation_constant_dataframe, x="elevation_constant", y="Average Empire Area")
            elev_const_vs_area.set(xlabel="Elevation Constant", ylabel="Average Empire Area")
            plot.show()

