import datetime
import re
from typing import List

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from scipy.stats import ttest_ind
from scipy.stats import mannwhitneyu
from sklearn.utils import resample


# general purpose: merge_data, process_data, pit_stop_group
def merge_data(_df_list: List[pd.DataFrame]) -> pd.DataFrame:
    """
    merges the dataframes according to their primary/foreign keys
    :param _df_list: list of dataframes to be merged
    :return: the merged dataframe
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


def process_data(mg_df: pd.DataFrame, normal_status=True) -> pd.DataFrame:
    """
    process the data for analysis:
    1. filter normal status
    2. add total laps for each record
    3. add total pit stops for each record
    4. calculate the proportion of lap when the driver pit for each pit record
    5. calculate how far the lap proportion deviates from the ideal even distribution for each pit record
    :param mg_df: the merged dataframe
    :param normal_status: if filter the dataframe with records that are finished or +? laps away from the finished
    :return: the processed dataframe
    """
    # 1. filtering normal status
    if normal_status:
        _status_select = [1, 11, 12, 13, 14, 15, 16, 17, 18, 19]
        mg_df.drop(mg_df[~mg_df['statusId'].isin(_status_select)].index, inplace=True)
    # 2&3. add total laps & total pit stops for each record
    _total_laps = mg_df[(mg_df['positionOrder'] == 1) & (mg_df['stop'] == 1)].reset_index(drop=True)[['raceId', 'laps']]
    _total_laps.columns = [str(_total_laps.columns[0]), 'total_laps']
    _total_stops = mg_df.groupby(by=['raceId', 'driverId'], as_index=False)['stop'].max()
    _total_stops.columns = list(_total_stops.columns[:2]) + ['total_stops']
    # 4. calculate the proportion of lap when the driver pit for each pit record
    mg_df = pd.merge(mg_df, _total_laps, on='raceId')
    mg_df = pd.merge(mg_df, _total_stops, on=['raceId', 'driverId'])
    # 5. calculate how far the lap proportion deviates from the ideal even distribution for each pit record
    mg_df['lap_prop'] = mg_df.apply(lambda x: x['lap'] / x['total_laps'], axis=1)
    mg_df['abs_deviation'] = mg_df.apply(lambda x: abs(x['stop'] / (x['total_stops'] + 1) - x['lap_prop']), axis=1)
    # 6. deviation mean, grouped by each driver in each race
    avg_deviation = pd.DataFrame(mg_df.groupby(['raceId', 'driverId'])['abs_deviation'].mean())
    avg_deviation = avg_deviation.add_suffix('_mean').reset_index()
    mg_df = pd.merge(mg_df, avg_deviation, on=['raceId', 'driverId'])
    return mg_df


def pit_stop_group(df: pd.DataFrame) -> dict:
    """
    group the records by the total number of pit stops of each racing record
    :param df: the merged and processed dataframe
    :return: a dictionary with total pit numbers as keys and dataframe of records as values
    """
    max_num = df['total_stops'].max()
    _df_dict = {}
    for i in range(1, max_num + 1):
        _df_dict[i] = df[df['total_stops'] == i][['stop', 'positionOrder', 'lap_prop']]
    return _df_dict


# hypothesis 1
# ...

# hypothesis 2: distribution_plot
def distribution_plot(_df_dict: dict, show_mean: bool = True, show_description: bool = True, save_fig: bool = False):
    """
    Hypothesis 2 Function
    draw histograms for dataframes grouped by total pit stops number and the order of pit stop
    :param _df_dict: the dictionary of dataframe, grouped using pit_stop_group
    :param show_mean: if to show vertical lines of mean on the histograms
    :param show_description: if to show distribution description
    :param save_fig: if to save as picture
    :return: None. Plots the distribution
    """
    # plot settings
    bins = np.linspace(0, 1, 50)
    color_bin = ['tab:blue', 'tab:orange', 'lightcoral']
    color_bin2 = ['deepskyblue', 'gold', 'crimson']

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
            if show_mean: plt.axvline(x=df_mean, color=color_bin2[plot_count], linewidth=4)
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
    :param show_mean: if to show vertical lines of mean on the histograms
    :param show_description: if to show descriptions of tests & distribution results
    :param show_divide: if to show points where the line is divided into even segments
    :param non_para: if to use non-parametric test
    :param save_fig: if to save as picture
    :return: None
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


def err_mean_plot(list_1: [pd.DataFrame], list_2: [pd.DataFrame], save_fig=False):
    """
    Hypothesis 3 Function
    :param list_1: the list of dataframes with position order in the front
    :param list_2: the list of dataframes with position order in the back
    :param save_fig: if to save as picture
    :return: None
    """
    bins = np.linspace(0, 1, 50)
    color_bin = ['deepskyblue', 'tab:orange', 'tomato']
    color_bin2 = ['steelblue', 'crimson', 'lavender']

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
        plt.hist(_df_back, bins, alpha=0.8, color=color_bin[2], label='Lower Ranking')
        plt.hist(_df_front, bins, alpha=0.8, color=color_bin[0], label='Higher Ranking')
        plt.legend(loc="upper left")

        _df_front_mean = round(_df_front.mean(), ndigits=3)
        _df_back_mean = round(_df_back.mean(), ndigits=3)

        plt.axvline(x=_df_front_mean, color=color_bin2[0], linewidth=4)
        plt.axvline(x=_df_back_mean, color=color_bin2[1], linewidth=4)

        sig_level = 0.05
        p_value = mannwhitneyu(_df_front, _df_back).pvalue
        print(f'Mann-Whitney U rank test p value={p_value}')

        if p_value < sig_level:
            print('     Mean of Average Deviations - ')
            print(f'        Higher Ranking: {_df_front_mean}, Lower Ranking: {_df_back_mean}')
            if _df_front_mean < _df_back_mean:
                print('Higher ranking records have significantly lower mean deviations')
            else:
                print('Lower ranking records have significantly lower mean deviations')
        if save_fig: plt.savefig(f'image/hypo3/err_mean.png', transparent=False)
        plt.show()
