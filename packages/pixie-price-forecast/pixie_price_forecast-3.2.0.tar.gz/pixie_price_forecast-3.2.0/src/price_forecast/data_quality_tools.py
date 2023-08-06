from datetime import datetime
import numpy as np
import pandas as pd
from price_forecast.data_quality_reference import province_mapping, column_names, agg_data, weighted_average, mode_dict
from price_forecast.queries_templates import query_read_data
from price_forecast.viz_tools import compare_cleansing


def fix_province_names(df: pd.DataFrame):
    unique_province = list(df[column_names['province']].unique())
    for old_name in unique_province:
        try:
            df.loc[df[column_names['province']] == old_name, column_names['province']] = \
                province_mapping[old_name.lower()]['name']
        except AttributeError:
            print('Name is nan')
        except KeyError:
            df.loc[df[column_names['province']] == old_name, column_names['province']] = np.nan
            print(f'Error: {old_name} - {old_name.lower()}')
    df.dropna(inplace=True, subset=[column_names['province']])
    prices_1 = df.groupby(agg_data['grouping_cols']).apply(weighted_average, 'mean_unitary_price', 'number_properties')
    prices_2 = df.groupby(agg_data['grouping_cols']).apply(weighted_average, 'median_unitary_price', 'number_properties')
    prices_3 = df.groupby(agg_data['grouping_cols']).apply(weighted_average, 'mean_price', 'number_properties')
    prices_4 = df.groupby(agg_data['grouping_cols']).apply(weighted_average, 'median_price', 'number_properties')
    df = df.groupby(agg_data['grouping_cols']).agg(agg_data['agg_funcs'])
    df['mean_unitary_price'] = prices_1
    df['median_unitary_price'] = prices_2
    df['mean_price'] = prices_3
    df['median_price'] = prices_4
    return df


def remove_daily_peaks(df: pd.DataFrame,
                       ref_col: str,
                       province_name: str,
                       debug: bool = False,
                       upper_bound: float = .95,
                       lower_bound: float = .05):
    """
    Remove peaks found in daily data.
    :param df: Data Frame to be processed.
    :param ref_col: Name of the column used to detect the outliers.
    :param province_name: Name of the target province.
    :param debug: If True it plots the raw and processed timeseries.
    :param upper_bound: Quantile above which any change filtered.
    :param lower_bound: Quantile below which any negative change will be filtered.
    :return: Clean time series.
    """
    province_col = column_names['province']
    datetime_col = column_names['date']
    df_loc = df.loc[df[province_col] == province_name, :]
    df_loc.set_index(datetime_col, inplace=True)
    df_loc.loc[:, 'n_pct_change'] = df_loc[ref_col].pct_change()
    df_ref = df_loc.copy(deep=True)
    mask = (df_loc.n_pct_change <= df_loc.n_pct_change.quantile(lower_bound)) | (
                df_loc.n_pct_change >= df_loc.n_pct_change.quantile(upper_bound))
    df_loc.loc[mask, ref_col] = np.nan
    df_loc[ref_col].fillna(method='ffill', inplace=True)
    if debug:
        compare_cleansing(df_ref=df_ref, df_filtered=df_loc, province_name=province_name, reference_column=ref_col)
    df_loc.drop('n_pct_change', axis=1, inplace=True)
    df_loc.reset_index(inplace=True)
    return df_loc


def remove_outliers(df: pd.DataFrame, debug: bool = False):
    """
    Iterates over all provinces and removes strange daily peaks
    :param df: All df
    :param debug:
    :return:
    """
    df.reset_index(inplace=True)
    results = list()
    for prov in df.province.unique():
        df_loc = remove_daily_peaks(df=df,
                                    ref_col='number_properties',
                                    province_name=prov,
                                    debug=debug)
        results.append(df_loc)
    results = pd.concat(results)
    return results


def remove_outliers_agg(df: pd.DataFrame):
    # Ad Hoc fix
    loc_col_names = ['number_properties', 'max_price', 'perc_price_99', 'perc_price_95', 'perc_price_90',
                     'perc_price_10', 'perc_price_05', 'perc_price_01', 'visits', 'leads',
                     'mean_unitary_price', 'median_unitary_price', 'mean_price', 'median_price']
    july = pd.to_datetime('2018-07-01')
    august = pd.to_datetime('2018-08-01')
    september = pd.to_datetime('2018-09-01')
    october = pd.to_datetime('2018-10-01')
    for province in df.province.unique():
        for col_name in loc_col_names:
            try:
                df.loc[(df.province == province) & (df.version_date == august), col_name] = \
                    df.loc[(df.province == province) & (df.version_date == july), col_name].values[0] * 0.67 + \
                    df.loc[(df.province == province) & (df.version_date == october), col_name].values[0] * 0.33
                df.loc[(df.province == province) & (df.version_date == september), col_name] = \
                    df.loc[(df.province == province) & (df.version_date == july), col_name].values[0] * 0.33 + \
                    df.loc[(df.province == province) & (df.version_date == october), col_name].values[0] * 0.67
            except IndexError:
                print(f'Skipping {province}-{col_name}')
    return df


def compute_mortgage_fee(df: pd.DataFrame, db_engine, differential: float = 0.015):
    euribor = pd.read_sql('price_euribor', db_engine)
    # Setting all dates to the same format
    euribor.date = pd.to_datetime(euribor.date)
    df.version_date = pd.to_datetime(df.version_date)
    euribor['euribor'] = euribor['euribor'] + differential
    df = df.merge(euribor, how='left', left_on='version_date', right_on='date')
    df.fillna(method='ffill', inplace=True)
    df.fillna(method='bfill', inplace=True)
    df['mean_price'] = df['mean_price'] * df['euribor'] / (1 - 1 / np.power(1 + df['euribor'], 30)) / 12
    df['median_price'] = df['median_price'] * df['euribor'] / (1 - 1 / np.power(1 + df['euribor'], 30)) / 12
    df.drop(['date', 'euribor'], axis=1, inplace=True)
    return df


def apply_data_cleansing(db_engine):
    target_table = 'price_clean_data'
    for mode, _ in mode_dict.items():
        print(f'** {mode} **')
        query = query_read_data(mode)
        df_ = pd.read_sql(query, db_engine)
        df_ = fix_province_names(df_)
        df_ = remove_outliers(df_, debug=False)
        if 'demand' in mode:
            df_ = remove_outliers_agg(df_)
        if 'pro' in mode:
            df_ = remove_outliers_agg(df_)
        if 'sell' in mode:
            df_ = compute_mortgage_fee(df=df_, db_engine=db_engine)
        df_['extraction_type'] = mode
        df_['tag_use'] = True
        df_['load_date'] = datetime.strftime(datetime.today(), '%Y-%m-%d')
        df_.to_sql(target_table, db_engine, if_exists='append', index=False)


if __name__ == '__main__':
    pass
