import pandas as pd
import matplotlib.pyplot as plt

def read_data(file: str) -> pd.DataFrame:
    """
    this function is used to turn csv file into dataframe
    :param file: input csv file name
    :return: dataframe of the input csv file
    """
    df = pd.read_csv(file)
    return df

def data_process(df:pd.DataFrame, column,value) -> pd.DataFrame:
    """
    this function used to import and process the data
    :param df: dataframe that need to process
    :param column: column that need to clean and convert data type
    :param value: rows with the value will be deleted
    :return: dataframe that are processed
    """
    df1= df.dropna()
    df2 = df1[df1[column].notna()]
    df2.drop(df2[df2[column] == value].index, inplace = True)
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
    return (pitstop_groupby)


def pitstop_boxplot(df_a, df_b, merge_key: list, boxplot_data: list):
    joined_table = df_a.merge(df_b, on = merge_key)
    boxplot_base = joined_table[boxplot_data]
    boxplot = boxplot_base.boxplot(by="stop")
    boxplot.plot()

    plt.show()
    # plt.title("")

    # return(output)




if __name__ == '__main__':
    pitstops_file = read_data("data/pit_stops.csv")
    results_file = read_data("data/results.csv")
    total_pitstop = total_pitstop(pitstops_file)
    process = data_process(results_file, "position", "\\N")
    plot = pitstop_boxplot(total_pitstop, process, ["raceId", "driverId"],["stop", "position"])
    # print(plot)



