import re
from typing import List

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from scipy.stats import ttest_1samp
from scipy.stats import ttest_ind
from scipy.stats import wilcoxon
from scipy.stats import mannwhitneyu
from sklearn.utils import resample


# general purpose: merge_data, process_data, pit_stop_group
def merge_data(_df_list: List[pd.DataFrame]) -> pd.DataFrame:
    """
    merges the dataframes according to their primary/foreign keys
    :param _df_list: list of dataframes to be merged
    :return: the merged dataframe

    >>> d1 = {'df_Id': [1, 2], 'd1_col': [3, 4]}
    >>> d2 = {'df_Id': [3, 2], 'd2_col': [8, 9]}
    >>> df1 = pd.DataFrame(data=d1)
    >>> df2 = pd.DataFrame(data=d2)
    >>> merge_data([df1, df2])
       df_Id  d1_col  d2_col
    0      1       3     NaN
    1      2       4     9.0
    >>> d1 = {'df_Id': [1, 2], 'd1_col': [3, 4]}
    >>> d2 = {'not_df_Id': [3, 2], 'd2_col': [8, 9]}
    >>> df1 = pd.DataFrame(data=d1)
    >>> df2 = pd.DataFrame(data=d2)
    >>> merge_data([df1, df2])
    Error: no common "id" columns found
       df_Id  d1_col
    0      1       3
    1      2       4
    >>> d1 = {'df_Id': [1, 2], 'd1_col': [3, 4]}
    >>> d2 = {'df_Id': [3, 2], 'd2_col': [8, 9]}
    >>> d3 = {'not_df_Id': [6, 6], 'd2_col': [6, 7]}
    >>> df1 = pd.DataFrame(data=d1)
    >>> df2 = pd.DataFrame(data=d2)
    >>> df3 = pd.DataFrame(data=d3)
    >>> merge_data([df1, df2, df3])
    Error: no common "id" columns found
       df_Id  d1_col  d2_col
    0      1       3     NaN
    1      2       4     9.0

    """
    # set up internal parameters
    suffixes = ['_1', '_2']
    r = re.compile('\w*Id')

    # set up variables based on input
    num = len(_df_list)  # length of the list
    to_select = list(range(1, num))  # list of indexes of dataframe to be merged
    remaining = set(range(1, num))  # set of remaining indexes of dataframes yet to be merged

    # get all the '<something>id' columns for each dataframe
    id_list = [set(filter(r.match, table)) for table in _df_list]
    # set up the merged dataframe, 'mg_df'
    mg_df = _df_list[0]
    mg_id = id_list[0]  # set the id set of the merged dataframe as the first dataframe's id set

    # start merging dataframes
    while True:
        merge_flag = 0  # flag indicating if a while-true run has merged any new dataframe
        for index in to_select:
            intersect = mg_id.intersection(id_list[index])
            all_col_intersect = set(mg_df.columns).intersection(set(_df_list[index].columns))
            # iterate through the remaining dataframe
            # and merge those with common id(s)
            if (index in remaining) and intersect:
                if all_col_intersect == intersect:
                    mg_df = pd.merge(mg_df, _df_list[index], on=list(intersect), how='left')
                else:
                    # if there are other common columns than the ids, set suffixes
                    mg_df = pd.merge(mg_df, _df_list[index], on=list(intersect), how='left', suffixes=suffixes)
                # add the new ids into the total id set of the merged dataframe
                mg_id = mg_id.union(set(id_list[index]))
                remaining.remove(index)  # remove the index of the added dataframe
                merge_flag = 1
        if not remaining:
            break  # break if there is no more dataframe to be added
        if not merge_flag:  # if no new dataframe was merged in this while-true run
            print('Error: no common "id" columns found')
            break  # breaks
    return mg_df


def process_data(mg_df: pd.DataFrame, normal_status=True, totals=True, deviation=True) -> pd.DataFrame:
    """
    process the data for analysis:
    1. filter normal status
    2. add total laps for each record
    3. add total pit stops for each record
    4. calculate the proportion of lap when the driver pit for each pit record
    5. calculate how far the lap proportion deviates from the ideal even distribution for each pit record
    6. calculate deviation mean, grouped by each driver in each race
    :param mg_df: the merged dataframe
    :param normal_status: if true, filter the dataframe with records that are finished or +? laps away from the finished
    :param totals: if true, calculate the total laps, total stops and lap proportions
    :param deviation: if true, calculate the deviations and the relevant statistics
    :return: the processed dataframe

    >>> test_df = pd.DataFrame({"raceId": [1]*5+[2]*4,\
                   "driverId": [1,1,1,2,3,4,4,5,5],\
                   "positionOrder": [1,1,1,2,3,1,1,5,5],\
                   "stop": [1,2,3,1,1,1,2,1,2],\
                   "lap": [2,5,8,5,5,3,6,3,6],\
                   "laps": [20]*9,\
                   "statusId": [1]*4+[2]+[1]*2+[11]*2})
    >>> process_data(test_df)
       raceId  driverId  positionOrder  ...  lap_prop  abs_deviation  abs_deviation_mean
    0       1         1              1  ...      0.10       0.150000               0.250
    1       1         1              1  ...      0.25       0.250000               0.250
    2       1         1              1  ...      0.40       0.350000               0.250
    3       1         2              2  ...      0.25       0.250000               0.250
    4       2         4              1  ...      0.15       0.183333               0.275
    5       2         4              1  ...      0.30       0.366667               0.275
    6       2         5              5  ...      0.15       0.183333               0.275
    7       2         5              5  ...      0.30       0.366667               0.275
    <BLANKLINE>
    [8 rows x 12 columns]
    """
    # 1. filtering normal status
    if normal_status:
        _status_select = [1, 11, 12, 13, 14, 15, 16, 17, 18, 19]
        mg_df.drop(mg_df[~mg_df['statusId'].isin(_status_select)].index, inplace=True)
    # 2&3. add total laps & total pit stops for each record
    if totals:
        _total_laps = mg_df[(mg_df['positionOrder'] == 1) & (mg_df['stop'] == 1)].reset_index(drop=True)[
            ['raceId', 'laps']]
        _total_laps.columns = [str(_total_laps.columns[0]), 'total_laps']
        _total_stops = mg_df.groupby(by=['raceId', 'driverId'], as_index=False)['stop'].max()
        _total_stops.columns = list(_total_stops.columns[:2]) + ['total_stops']
        mg_df = pd.merge(mg_df, _total_laps, on='raceId')
        mg_df = pd.merge(mg_df, _total_stops, on=['raceId', 'driverId'])
        # 4. calculate the proportion of lap when the driver pit for each pit record
        mg_df['lap_prop'] = mg_df.apply(lambda x: x['lap'] / x['total_laps'], axis=1)
        if deviation:
            # 5. calculate how far the lap proportion deviates from the ideal even distribution for each pit record
            mg_df['abs_deviation'] = mg_df.apply(lambda x: abs(x['stop'] / (x['total_stops'] + 1) - x['lap_prop']),
                                                 axis=1)
            # 6. deviation mean, grouped by each driver in each race
            avg_deviation = pd.DataFrame(mg_df.groupby(['raceId', 'driverId'])['abs_deviation'].mean())
            avg_deviation = avg_deviation.add_suffix('_mean').reset_index()
            mg_df = pd.merge(mg_df, avg_deviation, on=['raceId', 'driverId'])
    return mg_df


def pit_stop_group(df: pd.DataFrame, by='pit_order'):
    """
    1. by = 'pit_order': group the records by the total number of pit stops of each racing record
    2. by = 'total_stops': calculate the total number of pitstop for each driver per race
    :param by: group by what standard. 1. pit order (type a). 2. total pits (type b)
    :param df: the merged and processed dataframe
    :return: (type a): a dictionary with total pit numbers as keys and dataframe of records as values; (type b): a dataframe with positional info, grouped by the total pit stops of each driver from in race

    >>> test_df = pd.DataFrame({"raceId": [1]*5+[2]*4,\
                   "driverId": [1,1,1,2,3,4,4,5,5],\
                   "positionOrder": [1,1,1,2,3,1,1,5,5],\
                   "stop": [1,2,3,1,1,1,2,1,2],\
                   "lap": [2,5,8,5,5,3,6,3,6],\
                   "laps": [20]*9,\
                   "statusId": [1]*4+[2]+[1]*2+[11]*2})
    >>> test_df = process_data(test_df)
    >>> pit_stop_group(test_df)
    {1:    stop  positionOrder  lap_prop
    3     1              2      0.25, 2:    stop  positionOrder  lap_prop
    4     1              1      0.15
    5     2              1      0.30
    6     1              5      0.15
    7     2              5      0.30, 3:    stop  positionOrder  lap_prop
    0     1              1      0.10
    1     2              1      0.25
    2     3              1      0.40}
    >>> pit_stop_group(test_df, by='total_stops')
       raceId  driverId  positionOrder  total_stops
    0       1         1              1            3
    1       1         2              2            1
    2       2         4              1            2
    3       2         5              5            2
    """
    if by == 'pit_order':
        max_num = df['total_stops'].max()
        _df_dict = {}
        for i in range(1, max_num + 1):
            _df_dict[i] = df[df['total_stops'] == i][['stop', 'positionOrder', 'lap_prop']]
        return _df_dict
    elif by == 'total_stops':
        pitstop_df = df[["raceId", "driverId", 'positionOrder', "total_stops"]]
        _df_group = pitstop_df.groupby(["raceId", "driverId", 'positionOrder'], as_index=False)["total_stops"].count()
        _df_group["positionOrder"] = _df_group["positionOrder"].astype(int)
        _df_group.sort_values(by=["raceId", 'driverId'], inplace=True)
        return _df_group


def lap_data_process(df: pd.DataFrame, lap_df: pd.DataFrame) -> pd.DataFrame:
    """
    this function is used to process time spent on laps for each driver
    :param df: dataframe containing raceId, driverId and positionOrder
    :param lap_df: lap data to margin
    :return: the dataframe shows the standard deviation of time spent on laps for each driver in a race
    >>> test_df = pd.DataFrame({"raceId": [1]*8,"driverId": [1]*5+[2]*3,"positionOrder": [1]*5+[2]*3})
    >>> test_lap_df = pd.DataFrame({"raceId":[1]*8,"driverId":[1]*5+[2]*3,"milliseconds":['98109','100289','88132','283904','217333','189203','80103','163993']})
    >>> lap_data_process(test_df, test_lap_df)
       raceId  driverId  positionOrder  lap_time_STD
    0       1         1              1     80.584135
    1       1         2              2     49.467017

    """
    position_df = df[["raceId", "driverId", "positionOrder"]]
    joined_table = lap_df.merge(position_df, on=["raceId", "driverId"], how="left")
    joined_table["milliseconds"] = joined_table["milliseconds"].astype(int)
    # since most of the time spend for each lap is below 5 minutes, we assumed that the time spent greater than 5 minutes should be caused by accidents rather than strategy.
    # Thus, we focus on lap with time spend less than 6 minutes.
    joined_table= joined_table.loc[joined_table['milliseconds'] <= 360000]
    joined_table['lap_second']= joined_table['milliseconds'] /1000
    df_group = joined_table.groupby(["raceId", "driverId", 'positionOrder'], as_index=False)['lap_second'].std()
    df_group.sort_values(by=['raceId', 'positionOrder'], inplace=True)
    df_group.rename(columns={'lap_second': 'lap_time_STD'}, inplace=True)
    return df_group

# hypothesis 1: pitstop_boxplot, stop_chart, analysis_of_variance
def pitstop_boxplot(df: pd.DataFrame):
    """
    this function used to create the boxplot which shows the distribution of position for drivers taking different number of pit stop
    :param df: the dataframe grouped by driver and race
    :return: boxplot shows the distribution of position for drivers taking different number of pit stop
    >>> df = pd.DataFrame({"raceId":[1,2,2,4,6,7,3,3],"driverId":[1,2,3,4,5,6,7,1],'positionOrder':[3,4,5,1,2,2,1,3], "total_stops":[3,2,3,1,2,3,1,2]})
    >>> pitstop_boxplot(df)
    """
    boxplot_base = df[["total_stops", "positionOrder"]]
    boxplot = boxplot_base.boxplot(by="total_stops")
    boxplot.plot()
    plt.xlabel('Number of Pit Stops', fontsize='12')
    plt.ylabel('Position', fontsize='12')
    plt.title('Position Distribution by Pit Stops', fontsize='12')
    plt.tight_layout()
    plt.show()


def stop_chart(df: pd.DataFrame, pit_stop: int, max_position: int):
    """
    this function used to create bar chart which shows the number of drivers per position
    :param df: the dataframe grouped by driver and race
    :param pit_stop: number of pit stop the chart consider
    :param max_position: the maximum rank the chart show
    :return: bar chart shows the count of positions when taking 1, 2 or 3 pit stops
    >>> df = pd.DataFrame({"raceId":[1]*10,"driverId":[1,2,3,4,5,6,7,8,9,10],'positionOrder':[1,2,3,4,5,6,7,8,9,10], "total_stops":[1]*5+[2]*3+[3]*2})
    >>> stop_chart(df,3,10)
    """
    df_filtered = df[df['positionOrder'] <= max_position]
    for i in range(1, pit_stop + 1):
        position_count = df_filtered[df_filtered['total_stops'] == i].groupby(['positionOrder'])[
            "driverId"].count().reset_index(name='count')
        position_count.sort_values(by=['positionOrder'], inplace=True)
        position_count.plot.bar(x='positionOrder', y='count', fontsize='12')
        plt.xticks(fontsize='12', rotation=1)
        plt.xlabel('Position', fontsize='12', rotation=1)
        plt.ylabel('Number of drivers', fontsize='12')
        stop = "pit stop = " + str(i)
        plt.title(stop, fontsize='12')
        plt.show()


def analysis_of_variance(df: pd.DataFrame):
    """
    this function used to calculate the P-value of rank distribution when taking 1, 2 or 3 pit stops and check whether there is significant difference in rank distribution.
    :param df: the dataframe grouped by driver and race
    :return: the test result
    >>> df = pd.DataFrame({"raceId":[1,2,2,4,6,7,3,3],"driverId":[1,2,3,4,5,6,7,1],'positionOrder':[3,4,5,1,2,2,1,3], "total_stops":[3,2,3,1,2,3,1,2]})
    >>> analysis_of_variance(df)
    H0: There is no significant difference in rank distribution between drivers taking a different number of total pit stops.
    ----------------------------------------------------------------------------------------
    P-value between 1 pitstop and 2 pitstop is 0.1386406338132186
    H0 cannot be rejected
    ----------------------------------------------------------------------------------------
    P-value between 2 pitstop and 3 pitstop is 1.0
    H0 cannot be rejected
    ----------------------------------------------------------------------------------------
    P-value between 3 pitstop and 1 pitstop is 0.1386406338132186
    H0 cannot be rejected

    """
    print('H0: There is no significant difference in rank distribution between drivers taking a different number of '
          'total pit stops.')
    for i in range(1, 4):
        if i <= 2:
            filtered_df1 = df[df['total_stops'] == i]
            filtered_df2 = df[df['total_stops'] == i + 1]
            p_value = mannwhitneyu(filtered_df1['positionOrder'], filtered_df2['positionOrder']).pvalue
            print('-' * 88)
            print('P-value between {} pitstop and {} pitstop is {}'.format(i, i + 1, p_value))
            if p_value > 0.05:
                print("H0 cannot be rejected")
            else:
                print("Reject H0.", "There is a difference.")
        if i == 3:
            filtered_df1 = df[df['total_stops'] == i]
            filtered_df2 = df[df['total_stops'] == i - 2]
            p_value = mannwhitneyu(filtered_df1['positionOrder'], filtered_df2['positionOrder']).pvalue
            print('-' * 88)
            print('P-value between {} pitstop and {} pitstop is {}'.format(i, i - 2, p_value))
            if p_value > 0.05:
                print("H0 cannot be rejected")
            else:
                print("Reject H0.", "There is a difference.")


# hypothesis 2: distribution_plot
def distribution_plot(_df_dict: dict, show_mean: bool = True, show_description: bool = True,
                      save_fig: bool = False):
    """
    Hypothesis 2 Function
    draw histograms for dataframes grouped by total pit stops number and the order of pit stop
    :param _df_dict: the dictionary of dataframe, grouped using pit_stop_group
    :param show_mean: if true, show vertical lines of mean on the histograms
    :param show_description: if true, show distribution description
    :param save_fig: if true, save as picture
    :return: None. Plots the distribution

    >>> df = pd.DataFrame({"raceId": [1]*5+[2]*4,\
                   "driverId": [1,1,1,2,3,4,4,5,5],\
                   "positionOrder": [1,1,1,2,3,1,1,5,5],\
                   "stop": [1,2,3,1,1,1,2,1,2],\
                   "lap": [2,5,8,5,5,3,6,3,6],\
                   "laps": [20]*9,\
                   "statusId": [1]*4+[2]+[1]*2+[11]*2})
    >>> test_df = process_data(df)
    >>> test_df_dict = pit_stop_group(test_df)
    >>> distribution_plot(test_df_dict)
    ----------------------------------------------------------------------------------------
    Total Pit Stops:  1
    No.  1  pit stop:  mean =  0.25  std =  nan
        0.0% within mean ± 1 std
        0.0% within mean ± 2 std
         One sample T Test, mu=0.5, p value=nan
         One sample Wilcoxon Signed Rank Test, mu=0.5, p value=1.0
    ----------------------------------------------------------------------------------------
    Total Pit Stops:  2
    No.  1  pit stop:  mean =  0.15  std =  0.0
        100.0% within mean ± 1 std
        100.0% within mean ± 2 std
         One sample T Test, mu=0.333, p value=0.0
         One sample Wilcoxon Signed Rank Test, mu=0.333, p value=0.5
    No.  2  pit stop:  mean =  0.3  std =  0.0
        100.0% within mean ± 1 std
        100.0% within mean ± 2 std
         One sample T Test, mu=0.667, p value=0.0
         One sample Wilcoxon Signed Rank Test, mu=0.667, p value=0.5
    ----------------------------------------------------------------------------------------
    Total Pit Stops:  3
    No.  1  pit stop:  mean =  0.1  std =  nan
        0.0% within mean ± 1 std
        0.0% within mean ± 2 std
         One sample T Test, mu=0.25, p value=nan
         One sample Wilcoxon Signed Rank Test, mu=0.25, p value=1.0
    No.  2  pit stop:  mean =  0.25  std =  nan
        0.0% within mean ± 1 std
        0.0% within mean ± 2 std
         One sample T Test, mu=0.5, p value=nan
         One sample Wilcoxon Signed Rank Test, mu=0.5, p value=1.0
    No.  3  pit stop:  mean =  0.4  std =  nan
        0.0% within mean ± 1 std
        0.0% within mean ± 2 std
         One sample T Test, mu=0.75, p value=nan
         One sample Wilcoxon Signed Rank Test, mu=0.75, p value=1.0
    """
    # plot settings
    bins = np.linspace(0, 1, 50)
    color_bin = ['tab:blue', 'tab:orange', 'lightcoral']
    color_bin2 = ['deepskyblue', 'orangered', 'crimson']

    max_num_of_stops = 3  # consider only total pit stops = 1,2,3
    for ps_num in range(1, max_num_of_stops + 1):
        _df_tmp = _df_dict[ps_num]  # get dataframe of total pit stop = ps_num
        # _df_list: [<df: no.1 pit stop out of ps_num>, <df: no.2 pit stop out of ps_num>, ...]
        _df_list = [_df_tmp[_df_tmp['stop'] == i]['lap_prop'] for i in range(1, ps_num + 1)]

        if show_description:
            print('-' * 88)
        print('Total Pit Stops: ', ps_num)
        plot_count = 0
        plt.figure(figsize=(8, 6))
        plt.title(f'Frequency Distribution of Lap Proportions: Total Pit Stops = {ps_num}')
        plt.xlabel('Proportion of Total Laps')
        plt.ylabel('Record Frequency')
        for df in _df_list:
            # histogram
            plt.hist(df, bins, alpha=0.7, color=color_bin[plot_count], label=f'No.{plot_count + 1} pit stop')
            # mean, std calculation
            df_mean = round(df.mean(), ndigits=3)
            df_std = round(df.std(), ndigits=3)
            # show mean line (x = mean)
            # even dividing point:
            even_divide = (plot_count + 1) / (ps_num + 1)
            if show_mean:
                plt.axvline(x=df_mean, color=color_bin2[plot_count], linewidth=4)
                plt.axvline(x=even_divide, color='gold', linewidth=4)
            plot_count += 1
            # show distribution description
            if show_description:
                print('No. ', plot_count, ' pit stop: ', 'mean = ', df_mean, ' std = ', df_std)
                perc_1 = len(df[(df <= df_mean + df_std) & (df >= df_mean - df_std)]) / len(df)
                perc_2 = len(df[(df <= df_mean + 2 * df_std) & (df >= df_mean - 2 * df_std)]) / len(df)
                perc_1 = round(100 * perc_1, ndigits=1)
                perc_2 = round(100 * perc_2, ndigits=1)
                print(f'    {perc_1}% within mean ± 1 std')
                print(f'    {perc_2}% within mean ± 2 std')
                _test = ttest_1samp(a=df, popmean=even_divide)
                print(f'     One sample T Test, mu={round(even_divide, ndigits=3)}, p value={_test.pvalue}')
                _test = wilcoxon(df - even_divide)
                print(f'     One sample Wilcoxon Signed Rank Test, mu={round(even_divide, ndigits=3)}, '
                      f'p value={_test.pvalue}')
        # save as picture
        plt.legend(loc="upper left")
        if save_fig: plt.savefig(f'image/hypo2/distribution_{ps_num}.png')
        plt.show()


# hypothesis 3: front_back_division, comparison_plot
def front_back_division(mg_df: pd.DataFrame, select_col='lap_prop', max_pit=3, top_num=5):
    """
    Hypothesis 3 Function
    divide the dataframe into 2 groups: with positions before No.top_num(5) and after No.top_num(5).
    then, split each group into list
    :param mg_df: the merged and processed dataframe
    :param select_col: the numeric column to be studied
    :param max_pit: the maximum number of total pit stops in consideration
    :param top_num: the number (top 5) dividing the position orders as fronts and backs
    :return: the front list and the back list, in the form of:
    [<no.1 pit, total=1>, <no.1 pit, total=2>, <no.2 pit, total=2>, <no.1 pit, total=3>, ...]

    >>> df = pd.DataFrame({"raceId": [1]*5+[2]*4,\
                   "driverId": [1,1,1,2,3,4,4,5,5],\
                   "positionOrder": [1,1,1,2,10,1,1,13,13],\
                   "stop": [1,2,3,1,1,1,2,1,2],\
                   "lap": [2,5,8,5,5,3,6,3,6],\
                   "laps": [20]*9,\
                   "statusId": [1]*4+[2]+[1]*2+[11]*2})
    >>> test_df = process_data(df)
    >>> front_back_division(test_df)
    ([   stop  lap_prop
    3     1      0.25,    stop  lap_prop
    4     1      0.15,    stop  lap_prop
    5     2       0.3,    stop  lap_prop
    0     1       0.1,    stop  lap_prop
    1     2      0.25,    stop  lap_prop
    2     3       0.4], [Empty DataFrame
    Columns: [stop, lap_prop]
    Index: [],    stop  lap_prop
    6     1      0.15,    stop  lap_prop
    7     2       0.3, Empty DataFrame
    Columns: [stop, lap_prop]
    Index: [], Empty DataFrame
    Columns: [stop, lap_prop]
    Index: [], Empty DataFrame
    Columns: [stop, lap_prop]
    Index: []])
    >>> front_back_division(test_df, select_col='abs_deviation_mean')
    ([   total_stops  abs_deviation_mean
    3            1                0.25,    total_stops  abs_deviation_mean
    4            2               0.275,    total_stops  abs_deviation_mean
    0            3                0.25], [Empty DataFrame
    Columns: [total_stops, abs_deviation_mean]
    Index: [],    total_stops  abs_deviation_mean
    6            2               0.275, Empty DataFrame
    Columns: [total_stops, abs_deviation_mean]
    Index: []])
    """
    df_front = []
    df_back = []
    if select_col == 'abs_deviation_mean':
        df_select = mg_df[
            ['raceId', 'driverId', 'total_stops', 'positionOrder', 'abs_deviation_mean']].drop_duplicates()
        df_tmp = df_select[df_select['positionOrder'] <= top_num][['total_stops', 'abs_deviation_mean']]
        df_front = [df_tmp[df_tmp['total_stops'] == i] for i in range(1, max_pit + 1)]
        df_tmp = df_select[df_select['positionOrder'] > top_num][['total_stops', 'abs_deviation_mean']]
        df_back = [df_tmp[df_tmp['total_stops'] == i] for i in range(1, max_pit + 1)]
    else:
        for i in range(1, max_pit + 1):
            df_tmp = mg_df[mg_df['total_stops'] == i]
            for j in range(1, i + 1):
                df_select = df_tmp[df_tmp['stop'] == j]
                df_front.append(df_select[df_select['positionOrder'] <= top_num][['stop', select_col]])
                df_back.append(df_select[df_select['positionOrder'] > top_num][['stop', select_col]])

    return df_front, df_back


def comparison_plot(list_1: [pd.DataFrame], list_2: [pd.DataFrame], select_col='lap_prop',
                    show_mean=True, show_description=True, show_divide=True, non_para=False, save_fig=False):
    """
    Hypothesis 3 Function
    draw pairs of histograms for dataframes grouped by total pit stops number and the order of pit stop
    :param list_1: the list of dataframes with position order in the front
    :param list_2: the list of dataframes with position order in the back
    :param select_col: the numeric column to be studied
    :param show_mean: if true, show vertical lines of mean on the histograms
    :param show_description: if true, show descriptions of tests & distribution results
    :param show_divide: if true, show points where the line is divided into even segments
    :param non_para: if true, use non-parametric test
    :param save_fig: if true, save as picture
    :return: None

    >>> pit = pd.read_csv('data/pit_stops.csv')
    >>> results = pd.read_csv('data/results.csv')
    >>> status = pd.read_csv('data/status.csv')
    >>> test_df = merge_data([pit, results, status])
    >>> test_df = process_data(test_df)[:200]
    >>> df_front, df_back = front_back_division(test_df)
    >>> comparison_plot(df_front,df_back)
    ----------------------------------------------------------------------------------------
    Total Pits: 1, no.1 pit, p value=nan
    ----------------------------------------------------------------------------------------
    Total Pits: 2, no.1 pit, p value=0.5500522065849768
    ----------------------------------------------------------------------------------------
    Total Pits: 2, no.2 pit, p value=0.10989810168884662
    ----------------------------------------------------------------------------------------
    Total Pits: 3, no.1 pit, p value=0.843490486470722
    ----------------------------------------------------------------------------------------
    Total Pits: 3, no.2 pit, p value=0.15423974718402614
    ----------------------------------------------------------------------------------------
    Total Pits: 3, no.3 pit, p value=0.3097817821496505
    """
    bins = np.linspace(0, 1, 50)
    color_bin = ['tab:blue', 'tab:orange', 'tab:red']
    color_bin2 = ['deepskyblue', 'crimson', 'lavender']

    plot_index = [[1, 1], [2, 1], [2, 2], [3, 1], [3, 2], [3, 3]]
    plot_num = 6

    for _i in range(plot_num):
        _total = plot_index[_i][0]  # total pit stops
        _pit = plot_index[_i][1]  # pit stop number
        df_f = list_1[_i][select_col]  # front
        df_b = resample(list_2[_i][select_col],
                        replace=True, n_samples=len(df_f), random_state=123)  # back
        print('-' * 88)
        plt.figure(figsize=(12, 6))
        plt.title(f'Frequency Distribution of Lap Proportions: Total Pit Stops = {_total}, No.{_pit} pit stop')
        plt.xlabel('Proportion of Total Laps')
        plt.ylabel('Record Frequency')
        plt.hist(df_b, bins, alpha=0.8, color=color_bin[2], label='Lower Ranking')
        plt.hist(df_f, bins, alpha=0.8, color=color_bin[0], label='Higher Ranking')
        plt.legend(loc="upper left")

        df_f_mean = round(df_f.mean(), ndigits=3)
        df_b_mean = round(df_b.mean(), ndigits=3)
        if show_mean:
            plt.axvline(x=df_f_mean, color=color_bin2[0], linewidth=4)
            plt.axvline(x=df_b_mean, color=color_bin2[1], linewidth=4)
            if show_divide: plt.axvline(x=_pit / (_total + 1), color='gold', linewidth=4)
        if show_description:
            if not non_para:
                p_value = ttest_ind(df_f, df_b).pvalue
            else:
                p_value = mannwhitneyu(df_f, df_b).pvalue
            print(f'Total Pits: {_total}, no.{_pit} pit, p value={p_value}')

        if save_fig: plt.savefig(f'image/hypo3/distribution_{_total}_{_pit}.png', transparent=False)
        plt.show()


def avg_deviation_plot(list_1: [pd.DataFrame], list_2: [pd.DataFrame], save_fig=False):
    """
    Hypothesis 3 Function
    :param list_1: the list of dataframes with position order in the front
    :param list_2: the list of dataframes with position order in the back
    :param save_fig: if true, save as picture
    :return: None

    >>> pit = pd.read_csv('data/pit_stops.csv')
    >>> results = pd.read_csv('data/results.csv')
    >>> status = pd.read_csv('data/status.csv')
    >>> test_df = merge_data([pit, results, status])
    >>> test_df = process_data(test_df)[:200]
    >>> df_front, df_back = front_back_division(test_df, select_col='abs_deviation_mean')
    >>> avg_deviation_plot(df_front,df_back)
    """
    bins = np.linspace(0, 1, 50)
    color_bin = ['tab:blue', 'tab:orange', 'tab:red']
    color_bin2 = ['deepskyblue', 'crimson', 'lavender']

    num = len(list_1)
    for i in range(num):
        _df_front = list_1[i]['abs_deviation_mean']
        _df_back = list_2[i]['abs_deviation_mean']

        _df_back = resample(_df_back, replace=True, n_samples=len(_df_front), random_state=123)
        print('-' * 88)
        plt.figure(figsize=(12, 6))
        plt.title(f'Average Deviation Distribution, Total Pit Stops = {i + 1}')
        plt.xlabel('Average Deviation')
        plt.ylabel('Record Frequency (each driver from each race)')
        plt.hist(_df_back, bins, alpha=0.9, color=color_bin[2], label='Lower Ranking')
        plt.hist(_df_front, bins, alpha=0.9, color=color_bin[0], label='Higher Ranking')
        plt.legend(loc="upper left")

        _df_front_mean = round(_df_front.mean(), ndigits=3)
        _df_back_mean = round(_df_back.mean(), ndigits=3)

        plt.axvline(x=_df_front_mean, color=color_bin2[0], linewidth=4)
        plt.axvline(x=_df_back_mean, color=color_bin2[1], linewidth=4)

        sig_level = 0.05
        p_value = mannwhitneyu(_df_front, _df_back).pvalue
        print(f'Total Pit Stops = {i + 1}')
        print(f'Mann-Whitney U rank test p value={p_value}')

        if p_value < sig_level:
            print('     Means of Average Deviation - ')
            print(f'        Higher Ranking: {_df_front_mean}, Lower Ranking: {_df_back_mean}')
            if _df_front_mean < _df_back_mean:
                print('Higher ranking records have significantly lower mean deviations')
            else:
                print('Lower ranking records have significantly lower mean deviations')
        if save_fig:
            plt.savefig(f'image/hypo3/err_mean_{i}.png', transparent=False)
        plt.show()


# hypothesis 4
def rank_df_plt(df: pd.DataFrame, top_num = 5, threshold=0.05):
    """
    this function is used to separate the positionOrder to high ranking or low ranking,
    create histgram showing the correlation between the ranking of drivers against the lap time std,
    and calculate the Pvalue between high ranking drivers and low ranking drivers.
    :param df: the dataframe containing the standard deviation of time spent on laps for each driver in a race
    :param top_num: the number (top 5) dividing the position orders as high ranking and low ranking
    :param threshold: the threshold used to evalute whether H0 should be rejected
    :return: histgram showing the correlation between the ranking of drivers against the lap time std and whether there is difference in the distribution of lap times STD between the ranking of drivers.
    >>> test_df = pd.DataFrame({"raceId": [1]*8,"driverId": [1,2,3,4,5,6,7,8],"positionOrder": [1,2,3,4,5,6,7,8],"lap_time_STD":[2,5,1,3,4,2,3,6]})
    >>> rank_df_plt(test_df)
    H0: There is no significant difference in the distribution of lap times STD between the ranking of drivers.
    ----------------------------------------------------------------------------------------
    P-value between high ranking drivers and low ranking drivers is 0.9149990485758882.
    ----------------------------------------------------------------------------------------
    H0 cannot be rejected
    """
    print('H0: There is no significant difference in the distribution of lap times STD between the ranking of drivers.')
    rank_list = []
    df = df.assign(rank='')
    position_list = df['positionOrder'].tolist()

    for position in position_list:
        if position <= top_num:
            rank_list.append('High Rank')
        else:
            rank_list.append('Low Rank')

    df['rank'] = rank_list
    df_high = df.loc[df['rank'] == 'High Rank']['lap_time_STD']
    df_low = resample(df.loc[df['rank'] == 'High Rank']['lap_time_STD'], replace=True, n_samples=len(df_high), random_state=123)
    bins = np.linspace(0, 40, 20)
    color_bin = ['tab:blue', 'tab:orange', 'tab:red']
    plt.hist(df_low, bins, alpha=0.8, color=color_bin[2], label='Low Ranking')
    plt.hist(df_high, bins, alpha=0.8, color=color_bin[0], label='High Ranking')
    plt.title(f'Frequency Distribution of Lap time STD')
    plt.ylabel('Record Frequency')
    plt.xlabel('Lap time STD')
    plt.legend(loc="upper right")
    print(' ' * 88)
    plt.show()
    pvalue = mannwhitneyu(df_high,df_low).pvalue
    print('-' * 88)
    print('P-value between high ranking drivers and low ranking drivers is {}.'.format(pvalue))
    print('-' * 88)
    if pvalue < threshold:
        print("Reject H0.", "There is a difference.")
    else:
        print("H0 cannot be rejected")


def barchart_lapspeed(df: pd.DataFrame) -> plt:
    """
    this function is used to calculate the average standard deviation of time spent on laps for each position, and create the bar chart showing the distribution of the average STD
    :param df: the dataframe containing the standard deviation of time spent on laps for each driver in a race
    :return: bar chart showed the distribution of the average standard deviation of time spent on laps for each position
    >>> test_df = pd.DataFrame({"raceId": [1]*2,"driverId": [1,2],"positionOrder": [1,2],"lap_time_STD":[2,5]})
    >>> barchart_lapspeed(test_df)
    """

    df2 = df.groupby(['positionOrder'], as_index=False)["lap_time_STD"].mean()
    df2.plot.bar(x='positionOrder', y='lap_time_STD', fontsize='9', alpha=0.7, color=['tab:blue'])
    plt.xlabel('Position', fontsize='12', rotation=1)
    plt.ylabel('Mean of lap time STD', fontsize='12')
    plt.xticks(rotation=1)
    plt.title(f'Distribution of lap time by rank', fontsize='12')
    plt.show()


if __name__ == '__main__':
    # Load data
    pit = pd.read_csv('data/pit_stops.csv')
    results = pd.read_csv('data/results.csv')
    status = pd.read_csv('data/status.csv')
    lap = pd.read_csv("data/lap_times.csv")
    # Process the data files
    merge_df = merge_data([pit, results, status])
    merge_df = process_data(merge_df)
    df_dict = pit_stop_group(merge_df)
    lap_df = lap_data_process(results, lap)
    # Hypothesis 1
    df_group = pit_stop_group(merge_df, by='total_stops')
    pitstop_boxplot(df_group)
    stop_chart(df_group, 3, 22)
    analysis_of_variance(df_group)
    # Hypothesis 2
    distribution_plot(df_dict)
    # Hypothesis 3
    df_front, df_back = front_back_division(merge_df, top_num=5)
    comparison_plot(df_front, df_back)
    df_front, df_back = front_back_division(merge_df, select_col='abs_deviation_mean', top_num=5)
    avg_deviation_plot(df_front, df_back)
    # Hypothesis 4
    rank_df_plt(lap_df)
    barchart_lapspeed(lap_df)
