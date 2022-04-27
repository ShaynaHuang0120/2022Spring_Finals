import datetime
import re
from typing import List
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind
from scipy.stats import mannwhitneyu
from sklearn.utils import resample


def read_data(file: str) -> pd.DataFrame:
    """
    this function is used to turn csv file into dataframe
    :param file: input csv file name
    :return: dataframe of the input csv file
    """
    df = pd.read_csv(file)
    return df


def data_process(df: pd.DataFrame, column, value) -> pd.DataFrame:
    """
    this function used to import and process the data
    :param df: dataframe that need to process
    :param column: column that need to clean and convert data type
    :param value: rows with the value will be deleted
    :return: dataframe that are processed
    """
    df1 = df.dropna()
    df2 = df1[df1[column].notna()]
    df2.drop(df2[df2[column] == value].index, inplace=True)
    df2[column] = df2[column].astype(int)
    return df2


def total_pitstop(pitstop_table: pd.DataFrame):
    """
    this function used to calculate the number of pitstop for each driver per race
    :param pitstop_table: dataframe that need to find the total pit stop rows
    :return: dataframe shows the total number of pit stop of each driver and race
    >>> df = pd.DataFrame({"raceId":[1,1,1],"driverId":[1,1,1], "stop":[1,2,3]})
    >>> total_pitstop(df)
       raceId  driverId  stop
    0       1         1     3
    """
    pitstop_df = pitstop_table[["raceId", "driverId", "stop"]]
    pitstop_groupby = pitstop_df.groupby(["raceId", "driverId"], as_index=False)["stop"].count()
    # print(pitstop_groupby["stop"].sum())
    pitstop_groupby.sort_values(by=["raceId", 'driverId'], inplace=True)
    print(pitstop_groupby)
    return (pitstop_groupby)


def pitstop_boxplot(df_a, df_b):
    """
    this function used to create the boxplot which shows the race result of different amount of pit stop
    :param df_a: table to join
    :param df_b: table to join
    :param merge_key: tables are joined based on merge_key
    :param boxplot_data: data used for boxplot
    :return: boxplot shows the race result of different amount of pit stop
    """
    joined_table = df_a.merge(df_b, on=["raceId", "driverId"])
    boxplot_base = joined_table[["stop", "position"]]
    print(joined_table)
    # print(boxplot_base)
    # print(boxplot_base.loc[boxplot_base['stop']==1])
    boxplot = boxplot_base.boxplot(by="stop")
    # return boxplot
    boxplot.plot()
    plt.show()


def tables_combined(df_a, df_b, df_c, merge_key1: list, merge_key2, time_condition: int):
    """
    function used to combine three tables with time condition
    :param df_a:table to join
    :param df_b:table to join
    :param df_c:table to join
    :param merge_key1: table a and table b are joined based on merge_key 1
    :param merge_key2: the seconded join is based on the merge_key 2
    :param time_condition: year difference from current year
    :return: combined tables in the previous "time_condition" year
    """
    current_year = datetime.datetime.now().year  # get current year
    joined_table = pd.merge(pd.merge(df_a, df_b, on=merge_key1), df_c, on=merge_key2, how='left')
    decade_table = joined_table = joined_table.loc[(current_year - joined_table['year']) <= time_condition]
    decade_table["stop"] = decade_table["stop"].astype(int)
    # print(decade_table[['year', "circuitId"]])
    print(decade_table)
    return decade_table


# Question: do we need to consider circuit id?
def stop_chart(combined_table: pd.DataFrame, pit_stop: int):
    """

    :param combined_table:
    :param df_a: table to join
    :param df_b: table to join
    :param df_c: table to join
    :param merge_key1: table a and table b are joined based on merge_key 1
    :param merge_key2: the seconded join is based on the merge_key 2
    :param pit_stop: number of pit stop we want to explore
    :return: bar chart shows the count of positions in history records when taking 1, 2 or 3 pit stops
    """

    for i in range(1, pit_stop + 1):
        position_count = combined_table[combined_table['stop'] == i].groupby(['position'])[
            "driverId"].count().reset_index(name='count')
        position_count.plot.bar(x='position', y='count', fontsize='9')
        # plt.xticks(rotation='90')
        stop = "pit stop = " + str(i)
        plt.title(stop)
        plt.show()


# def circuit_stop_chart(combined_table:pd.DataFrame, pit_stop: int):


if __name__ == '__main__':
    pitstops_file = read_data("../data/pit_stops.csv")
    results_file = read_data("../data/results.csv")
    races_file = read_data("../data/races.csv")
    total_pitstop = total_pitstop(pitstops_file)
    # total_pitstop(pitstops_file)
    process = data_process(results_file, "position", "\\N")
    pitstop_boxplot(total_pitstop, process)
    combined_table = tables_combined(process, total_pitstop, races_file, ["raceId", "driverId"], ['raceId'], 10)
    stop_chart(combined_table, 3)
