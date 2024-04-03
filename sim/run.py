
import mesa
import pandas
import seaborn as sns
from matplotlib import pyplot as plot
import math

from model import EuropeModel

hex_to_meters = 863000000

# parameters to run the batch run tests over
# format is {"<parameter name>": <single value of list of values>, ...}

# columns to include in the spreadsheet output
# have to have the same names as the reporters in the model's datacollector
default_columns = ['Average Empire Area (Hexes)', 'Average Empire Area (m^2)', 'Number of Empires', "5-50 Hexes",
                   "51-100 Hexes", "101-150 Hexes", "151-200 Hexes", "201-250 Hexes",
                   "251-300 Hexes", "301-350 Hexes", "351-400 Hexes", "401-450 Hexes",
                   "451-500 Hexes", "501-550 Hexes", "551-600 Hexes", "601 or more Hexes"]


if __name__ == '__main__':

    prompt_text = ("1. Model Modification Test\n"
                   "2. Power Decline Tests\n"
                   "3. Starting Position Tests\n"
                   "4. Delta Power Tests\n"
                   "5. Asabiya Growth Tests\n"
                   "6. Asabiya Decay Tests\n"
                   "7. Use Elevation Tests\n"
                   "8. Times Changed Hands Tests\n"
                   "9. Elevation Constant Tests\n"
                   "10. Logged Area Distribution Tests\n"
                   "11. Elev Constant / Power Decline Combo Tests\n")
    test = input(prompt_text)

    match test:
        case "1":
            ticks = 1
            model = EuropeModel(sim_length=ticks)
            for x in range(ticks):
                model.step()
        case "2":
            # parameters = {"power_decline": [x for x in range(1, 9)]}
            parameters = {"power_decline": [x / 10.0 for x in range(1, 81)]}
            data = mesa.batch_run(model_cls=EuropeModel, parameters=parameters, number_processes=8, max_steps=400, iterations=3)

            columns = ['power_decline']
            dataframe = pandas.DataFrame(data=data, columns=(columns + default_columns))
            dataframe.to_csv(path_or_buf='output_data/power_decline.csv', index_label="trial")

            pd = sns.pairplot(data=dataframe, x_vars=['power_decline'], y_vars=['Average Empire Area (Hexes)', 'Number of Empires'])
            plot.show()

        case "3":
            parameters = {"power_decline": 4.5}
            data = mesa.batch_run(model_cls=EuropeModel, parameters=parameters, number_processes=8, max_steps=400, iterations=200)

            columns = ['starting x', 'starting y']
            dataframe = pandas.DataFrame(data=data, columns=(columns + default_columns))
            dataframe.to_csv(path_or_buf="output_data/starting_point.csv", index_label="trial")

            sns.pairplot(data=dataframe, x_vars=['starting x', 'starting y'], y_vars=['Average Empire Area (Hexes)'], height=5, aspect=1)
            plot.show()
        case "4":
            parameters = {"delta_power": [x / 100.0 for x in range(1, 21)]}
            data = mesa.batch_run(model_cls=EuropeModel, parameters=parameters, number_processes=8, max_steps=400, iterations=5)

            columns = ['delta_power']
            dataframe = pandas.DataFrame(data=data, columns=(columns + default_columns))
            dataframe.to_csv(path_or_buf="output_data/delta_power.csv", index_label="trial")

            ad = sns.pairplot(data=dataframe, kind="reg", x_vars=["delta_power"], y_vars=["Average Empire Area (Hexes)", "Number of Empires"], height=5, aspect=1)
            plot.show()
        case "5":
            parameters = {"asa_growth": [x / 100.0 for x in range(1, 31)]}
            data = mesa.batch_run(model_cls=EuropeModel, parameters=parameters, number_processes=8, max_steps=400, iterations=5)

            columns = ['asa_growth']
            dataframe = pandas.DataFrame(data=data, columns=(columns + default_columns))
            dataframe.to_csv(path_or_buf="output_data/asa_growth.csv", index_label="trial")

            ag = sns.pairplot(data=dataframe, x_vars=["asa_growth"], y_vars=["Average Empire Area (Hexes)", "Number of Empires"], height=5, aspect=1)
            plot.show()
        case "6":
            parameters = {"asa_decay": [x / 100.0 for x in range(1, 31)]}
            data = mesa.batch_run(model_cls=EuropeModel, parameters=parameters, number_processes=8, max_steps=400, iterations=5)

            columns = ['asa_decay']
            dataframe = pandas.DataFrame(data=data, columns=(columns + default_columns))
            dataframe.to_csv(path_or_buf="output_data/asa_decay.csv", index_label="trial")

            ad = sns.pairplot(data=dataframe, x_vars=["asa_decay"], y_vars=["Average Empire Area (Hexes)", "Number of Empires"], height=5, aspect=1)
            plot.show()
        case "7":
            parameters = {"use_elevation": [True, False], "power_decline": [x / 10.0 for x in range(1, 81)]}
            data = mesa.batch_run(model_cls=EuropeModel, parameters=parameters, number_processes=8, max_steps=400, iterations=3)

            columns = ['use_elevation', 'power_decline']
            dataframe = pandas.DataFrame(data=data, columns=(columns + default_columns))
            dataframe.to_csv(path_or_buf="output_data/use_elevation.csv", index_label="trial")
        case "8":
            params = {"elevation_constant": [x for x in range(0, 10)]}
            data = mesa.batch_run(model_cls=EuropeModel, parameters=params, number_processes=8, max_steps=400, iterations=1)

            dataframe = pandas.DataFrame(data, columns=["Elevation", "Times Changed Hands", "Elevation Constant"])
            elev_vs_times = sns.lmplot(data=dataframe, x="Elevation", y="Times Changed Hands", hue="Elevation Constant", scatter=False)
            plot.show()

        case "9":
            parameters = {"elevation_constant": [x / 2 for x in range(0, 20)]}
            data = mesa.batch_run(model_cls=EuropeModel, parameters=parameters, number_processes=8, max_steps=400, iterations=5)

            columns = ['elevation_constant']
            dataframe = pandas.DataFrame(data=data, columns=(columns + default_columns))
            dataframe.to_csv(path_or_buf="output_data/elevation_constant.csv", index_label="trial")

            elev = sns.pairplot(data=dataframe, x_vars=["elevation_constant"], y_vars=["Average Empire Area (Hexes)", "Number of Empires"], height=5, aspect=1)
            plot.show()
        case "10":
            params = [x / 2 for x in range(0, 20)]
            ticks = 400
            for elev in params:
                model = EuropeModel(sim_length=ticks, elevation_constant=elev)
                for x in range(ticks):
                    model.step()

                areas = []
                for empire in [empire for empire in model.empires if empire.size > 5]:
                    areas.append(math.log(empire.size * hex_to_meters))

                elev_vs_times = sns.histplot(data=areas)
                elev_vs_times.set(title=f"elevation constant: {elev}", xlabel="ln(area)", ylabel="Frequency")
                plot.show()
        case "11":
            # parameters = {"power_decline": [2, 4], "elevation_constant": [2, 4, 6, 8]}
            parameters = {"power_decline": [x for x in range(1, 9)], "elevation_constant": [y for y in range(0, 10)]}
            data = mesa.batch_run(model_cls=EuropeModel, parameters=parameters, number_processes=8, max_steps=400, iterations=1)

            columns = ['elevation_constant', 'power_decline']
            dataframe = pandas.DataFrame(data=data, columns=(columns + default_columns))

            elev_and_pd = sns.pairplot(data=dataframe, x_vars=["elevation_constant"], y_vars=["Average Empire Area (Hexes)"], height=5, aspect=1, hue="power_decline")
            plot.show()
