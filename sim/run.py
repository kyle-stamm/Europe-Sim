
import mesa
import pandas

from model import EuropeModel

# ticks = 1
# model = EuropeModel(power_decline=1.4, sim_length=ticks)
# for x in range(ticks):
#     model.step()

# parameters to run the batch run tests over
# format is {"<parameter name>": <single value of list of values>, ...}
power_decline_test_parameters = {"power_decline": [x / 10.0 for x in range(1, 81)]}
starting_point_test_parameters = {"power_decline": 4.0}

# columns to include in the spreadsheet output
# have to have the same names as the reporters in the model's datacollector
area_vs_power_decline_columns = ['power_decline', 'Average Empire Area']
num_empires_columns = ['power_decline', 'Number of Empires']
area_histogram_columns = ["power_decline", "5-50 Hexes", "51-100 Hexes", "101-150 Hexes", "151-200 Hexes",
                          "201-250 Hexes", "251-300 Hexes", "301-350 Hexes", "351-400 Hexes", "401-450 Hexes",
                          "451-500 Hexes", "501-550 Hexes", "551-600 Hexes", "601 or more Hexes"]
starting_point_columns = ['starting x', 'starting y', 'Average Empire Area']

if __name__ == '__main__':

    test = input("1 for power decline tests, 2 for starting position tests\n")
    if test == "1":
        data = mesa.batch_run(model_cls=EuropeModel, parameters=power_decline_test_parameters, number_processes=8, max_steps=400, iterations=3)

        num_empires_dataframe = pandas.DataFrame(data=data, columns=num_empires_columns)
        num_empires_dataframe.to_csv(path_or_buf="output_data/num_empires_vs_power_decline.csv", index_label="trial")

        area_histogram_dataframe = pandas.DataFrame(data=data, columns=area_histogram_columns)
        area_histogram_dataframe.to_csv(path_or_buf="output_data/area_histogram_vs_power_decline.csv", index_label="trial")

        area_dataframe = pandas.DataFrame(data=data, columns=area_vs_power_decline_columns)
        area_dataframe.to_csv(path_or_buf='output_data/area_vs_power_decline.csv', index_label="trial")
    elif test == "2":
        data = mesa.batch_run(model_cls=EuropeModel, parameters=starting_point_test_parameters, number_processes=8, max_steps=400, iterations=240)

        starting_point_dataframe = pandas.DataFrame(data=data, columns=starting_point_columns)
        starting_point_dataframe.to_csv(path_or_buf="output_data/starting_point_vs_area.csv", index_label="trial")
