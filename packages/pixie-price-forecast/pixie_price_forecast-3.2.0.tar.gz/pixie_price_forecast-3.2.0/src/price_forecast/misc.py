from datetime import datetime
import pandas as pd
import numpy as np
from price_forecast.data_quality_reference import mode_dict
from price_forecast.queries_templates import query_read_data, reset_use_tag
from price_forecast.etl import setup_tunnel, create_pixie_engine


DATA_REF = {'arima_offer_rent':
                {'path': '../data/forecast_results/arima_demand_rent_rent.csv',
                 'name': 'offer_arima_rent',
                 'forecast': 'arima',
                 'forecast_up': 'arima_up',
                 'forecast_down': 'arima_down',
                 'target_name': 'mean_price'},
            'arima_demand_rent':
                {'path': '../data/forecast_results/arima_offer_rent_rent.csv',
                 'name': 'demand_arima_rent',
                 'forecast': 'arima',
                 'forecast_up': 'arima_up',
                 'forecast_down': 'arima_down',
                 'target_name': 'mean_price'},
            'arima_pro_rent':
                {'path': '../data/forecast_results/arima_pro_rent_rent.csv',
                 'name': 'pro_arima_rent',
                 'forecast': 'arima',
                 'forecast_up': 'arima_up',
                 'forecast_down': 'arima_down',
                 'target_name': 'mean_price'},
            'arima_demand_sell':
                {'path': '../data/forecast_results/arima_demand_sell_sell.csv',
                 'name': 'demand_arima_sell',
                 'forecast': 'arima',
                 'forecast_up': 'arima_up',
                 'forecast_down': 'arima_down',
                 'target_name': 'mean_unitary_price'},
            'arima_offer_sell':
                {'path': '../data/forecast_results/arima_offer_sell_sell.csv',
                 'name': 'offer_arima_sell',
                 'forecast': 'arima',
                 'forecast_up': 'arima_up',
                 'forecast_down': 'arima_down',
                 'target_name': 'mean_unitary_price'},
            'arima_pro_sell':
                {'path': '../data/forecast_results/arima_pro_sell_sell.csv',
                 'name': 'pro_arima_sell',
                 'forecast': 'arima',
                 'forecast_up': 'arima_up',
                 'forecast_down': 'arima_down',
                 'target_name': 'mean_unitary_price'},
            'rf_offer_rent':
                {'path': '../data/forecast_results/random_forest_demand_rent_rent.csv',
                 'name': 'offer_rf_rent',
                 'forecast': 'random_forest',
                 'forecast_up': 'random_forest_up',
                 'forecast_down': 'random_forest_down',
                 'target_name': 'mean_price'},
            'rf_demand_rent':
                {'path': '../data/forecast_results/random_forest_offer_rent_rent.csv',
                 'name': 'demand_rf_rent',
                 'forecast': 'random_forest',
                 'forecast_up': 'random_forest_up',
                 'forecast_down': 'random_forest_down',
                 'target_name': 'mean_price'},
            'rf_pro_rent':
                {'path': '../data/forecast_results/random_forest_pro_rent_rent.csv',
                 'name': 'pro_rf_rent',
                 'forecast': 'random_forest',
                 'forecast_up': 'random_forest_up',
                 'forecast_down': 'random_forest_down',
                 'target_name': 'mean_price'},
            'rf_demand_sell':
                {'path': '../data/forecast_results/random_forest_demand_sell_sell.csv',
                 'name': 'demand_rf_sell',
                 'forecast': 'random_forest',
                 'forecast_up': 'random_forest_up',
                 'forecast_down': 'random_forest_down',
                 'target_name': 'mean_unitary_price'},
            'rf_offer_sell':
                {'path': '../data/forecast_results/random_forest_offer_sell_sell.csv',
                 'name': 'offer_rf_sell',
                 'forecast': 'random_forest',
                 'forecast_up': 'random_forest_up',
                 'forecast_down': 'random_forest_down',
                 'target_name': 'mean_unitary_price'},
            'rf_pro_sell':
                {'path': '../data/forecast_results/random_forest_pro_sell_sell.csv',
                 'name': 'pro_rf_sell',
                 'forecast': 'random_forest',
                 'forecast_up': 'random_forest_up',
                 'forecast_down': 'random_forest_down',
                 'target_name': 'mean_unitary_price'},
            'nn_offer_rent':
                {'path': '../data/forecast_results/nn_demand_rent_rent.csv',
                 'name': 'offer_nn_rent',
                 'forecast': 'nn',
                 'forecast_up': 'nn_up',
                 'forecast_down': 'nn_down',
                 'target_name': 'mean_price'},
            'nn_demand_rent':
                {'path': '../data/forecast_results/nn_offer_rent_rent.csv',
                 'name': 'demand_nn_rent',
                 'forecast': 'nn',
                 'forecast_up': 'nn_up',
                 'forecast_down': 'nn_down',
                 'target_name': 'mean_price'},
            'nn_pro_rent':
                {'path': '../data/forecast_results/nn_pro_rent_rent.csv',
                 'name': 'rent_nn_pro',
                 'forecast': 'nn',
                 'forecast_up': 'nn_up',
                 'forecast_down': 'nn_down',
                 'target_name': 'mean_price'},
            'nn_demand_sell':
                {'path': '../data/forecast_results/nn_demand_sell_sell.csv',
                 'name': 'demand_nn_sell',
                 'forecast': 'nn',
                 'forecast_up': 'nn_up',
                 'forecast_down': 'nn_down',
                 'target_name': 'mean_unitary_price'},
            'nn_offer_sell':
                {'path': '../data/forecast_results/nn_offer_sell_sell.csv',
                 'name': 'offer_nn_sell',
                 'forecast': 'nn',
                 'forecast_up': 'nn_up',
                 'forecast_down': 'nn_down',
                 'target_name': 'mean_unitary_price'},
            'nn_pro_sell':
                {'path': '../data/forecast_results/nn_pro_sell_sell.csv',
                 'name': 'pro_nn_sell',
                 'forecast': 'nn',
                 'forecast_up': 'nn_up',
                 'forecast_down': 'nn_down',
                 'target_name': 'mean_unitary_price'}
            }
DATA_DRIVERS = {''}
NEW_DATA = {'reference_file': 'new_data.csv',
            'col_names': {'price': 'mean_unitary_price', 'date': 'version_date', 'province': 'province'},
            'input': {'offer': {'path': 'agg_prices_demand_oct.csv'},
                      'demand': {'path': 'agg_prices_offer_oct.csv'},
                      'pro': {'path': 'agg_prices_pro_oct.csv'},
                      'house': {'path': 'agg_prices_houses_oct.csv'}}}
INPUT_DATA = {
    'input': {
        'sell_flat_offer': {'path': '../data/clean_data/agg_prices_offer_sell.csv'},
        'sell_flat_demand': {'path': '../data/clean_data/agg_prices_demand_sell.csv'},
        'sell_flat_pro': {'path': '../data/clean_data/agg_prices_pro_sell.csv'},
        'rent_flat_offer': {'path': '../data/clean_data/agg_prices_offer_rent.csv'},
        'rent_flat_demand': {'path': '../data/clean_data/agg_prices_demand_rent.csv'},
        'rent_flat_pro': {'path': '../data/clean_data/agg_prices_pro_rent.csv'},
        'sell_house_offer': {'path': '../data/clean_data/agg_prices_offer_houses_sell.csv'},
        'sell_house_demand': {'path': '../data/clean_data/agg_prices_demand_houses_sell.csv'},
        'sell_house_pro': {'path': '../data/clean_data/agg_prices_pro_houses_sell.csv'},
        # 'rent_house_offer': {'path': '../data/clean_data/agg_prices_offer_houses_rent.csv'},
        'rent_house_demand': {'path': '../data/clean_data/agg_prices_demand_houses_rent.csv'},
        'rent_house_pro': {'path': '../data/clean_data/agg_prices_pro_houses_rent.csv'},
    },
    'vars': {
        'target': 'mean_unitary_price',
        'median_target': 'median_unitary_price',
        'total_target': 'mean_price',
        'total_median_target': 'median_price',
        'visit': 'visits',
        'n_properties': 'number_properties',
        'province': 'province',
        'version_date': 'version_date'}}


def join_datasets(db_engine,
                  date_col: str = 'datetime',
                  province_col: str = 'province'):
    """
    Join all predictions into a single dataset for reporting purposes.
    :param db_engine: Engine to connect to datavenues.
    :param date_col: Name of the common date column.
    :param province_col: Name of the common column containing province.
    :return: Save results in price_viz_forecast
    """
    all_df = list()
    for mode_name, _ in mode_dict.items():
        print(mode_name)
        models = ['nn', 'random_forest', 'arima']
        df = pd.read_sql(query_read_data(table_name='price_forecasts', mode=mode_name, use_tag=True), db_engine)
        for mod in models:
            df_model = df.loc[df.model == mod, :]

            df_model.rename({'forecast': mode_name + f'_{mod}',
                             'forecast_up': mode_name + f'_up_{mod}',
                             'forecast_down': mode_name + f'_down_{mod}',
                             'target': mode_name + f'_history_{mod}'}, axis=1, inplace=True)
            col_to_preserve = [mode_name + f'_{mod}',
                               mode_name + f'_up_{mod}',
                               mode_name + f'_down_{mod}',
                               mode_name + f'_history_{mod}', date_col, province_col]
            all_df.append(df_model[col_to_preserve])
    result = all_df[0]
    i = 1
    for df in all_df[1:]:
        print(i)
        result = result.merge(df, how='outer', on=[date_col, province_col])
        i += 1
    result['forecast_date'] = datetime.strftime(datetime.today(), '%Y-%m-%d')
    result['tag_use'] = True
    q = reset_use_tag('price_viz_forecast')
    db_engine.execute(q)
    result.to_sql('price_viz_forecast', db_engine, if_exists='append', index=False)


def create_column_mapping(suffix_name: str) -> dict:
    col_mapping = dict()
    for new_name, old_name in INPUT_DATA['vars'].items():
        if new_name in ('target', 'median_target', 'total_target', 'total_median_target', 'visit', 'n_properties'):
            col_mapping[old_name] = '_'.join([new_name, suffix_name])
        else:
            col_mapping[old_name] = new_name
    return col_mapping


def join_all_inputs(db_engine):
    df_all = list()
    for mode_name, _ in mode_dict.items():
        print(mode_name)
        df_loc = pd.read_sql(query_read_data(table_name='price_clean_data', mode=mode_name, use_tag=True), db_engine)
        col_mapping = create_column_mapping(suffix_name=mode_name)
        col_new_names = list(col_mapping.values())
        df_loc.rename(col_mapping, inplace=True, axis=1)
        df_loc = df_loc[col_new_names]
        df_all.append(df_loc)
    result = df_all[0]
    for df in df_all[1:]:
        result = result.merge(df, how='outer', on=['version_date', 'province'])
    result['version_date'] = pd.to_datetime(result['version_date'])
    result = result.groupby(['province', result.version_date.dt.year, result.version_date.dt.month]).mean()
    result.index.names = ['province', 'year', 'month']
    result = result.reset_index()
    result['version_date'] = pd.to_datetime([f'{i[0]}-{i[1]}-1' for i in zip(result['year'], result['month'])])
    result.drop(['year', 'month'], axis=1, inplace=True)
    result['price_diff_perc_sell'] = 100 * (result['target_offer_flat_sell'] - result['target_demand_flat_sell']) / \
                                     result['target_offer_flat_sell']
    result['price_diff_perc_rent'] = 100 * (result['target_offer_flat_rent'] - result['target_demand_flat_rent']) / \
                                     result['target_offer_flat_rent']
    result['visits_diff_perc'] = 100 * (result['visit_offer_flat_sell'] - result['visit_demand_flat_sell']) / \
                                 result['visit_offer_flat_sell']
    result.sort_values(['province', 'version_date'], inplace=True)
    result['lag_6'] = result.groupby(['province'])['target_offer_flat_sell'].diff(6).fillna(0)
    result['lag_3'] = result.groupby(['province'])['target_offer_flat_sell'].diff(3).fillna(0)
    result['lag_2'] = result.groupby(['province'])['target_offer_flat_sell'].diff(2).fillna(0)
    result['lag_1'] = result.groupby(['province'])['target_offer_flat_sell'].diff().fillna(0)
    result['tag_use'] = True
    result['extraction_date'] = datetime.strftime(datetime.today(), '%Y-%m-%d')
    q = reset_use_tag('price_viz_inputs')
    db_engine.execute(q)
    result.to_sql('price_viz_inputs', db_engine, if_exists='append', index=False)


def append_new_data(value_date: str):
    """
    Combining source data of the last month by province. It is set in NEW_DATA dictionary.
    :param value_date: Name of the last month.
    :return: Source data of the last month. new_data.csv
    """
    list_df = list()
    for name_agg, data_agg in NEW_DATA['input'].items():
        df_loc = pd.read_csv(data_agg['path'])
        df_loc.rename({NEW_DATA['col_names']['price']: name_agg}, axis=1, inplace=True)
        df_loc = df_loc.loc[:, [name_agg, NEW_DATA['col_names']['date'], NEW_DATA['col_names']['province']]]
        list_df.append(df_loc)
    output = list_df[0]
    for loc_df in list_df[1:]:
        output = output.merge(loc_df,
                              on=[NEW_DATA['col_names']['date'], NEW_DATA['col_names']['province']],
                              how='outer')
    output[NEW_DATA['col_names']['date']] = value_date
    try:
        df = pd.read_csv(NEW_DATA['reference_file'])
        df = df.append(output)
    except FileNotFoundError as e:
        print(e)
        df = output
    df = df.groupby([NEW_DATA['col_names']['date'], NEW_DATA['col_names']['province']]).mean().reset_index()
    df.to_csv(NEW_DATA['reference_file'], index=False)


def comparison_forecast_results():
    """
    Comparing results with forecast.
    :return: compare_results.csv
    """
    df_forecasts_october = pd.read_csv('merge_results.csv')
    df_forecasts_october.rename({'datetime': 'version_date'}, axis=1, inplace=True)
    df_forecasts_october = df_forecasts_october[['version_date', 'province',
                                                 'demand_arima', 'offer_arima', 'pro_arima', 'house_arima',
                                                 'demand_rf', 'offer_rf', 'pro_rf', 'house_rf',
                                                 'demand_nn', 'offer_nn', 'pro_nn', 'house_nn']]
    source = ['demand', 'offer', 'pro', 'house']
    model = ['arima', 'rf', 'nn']
    source, model = np.meshgrid(source, model)
    df_results = pd.read_csv('new_data.csv')
    list_df = list()
    for src, mod in zip(source.flatten(), model.flatten()):
        try:
            pred_col = '_'.join([src, mod])
            df_loc = df_forecasts_october[['version_date', 'province', pred_col]]
            df_loc.rename({pred_col: 'forecast'}, axis=1, inplace=True)
            df_loc['model'] = mod
            df_loc['source'] = src
            df_loc.dropna(inplace=True)
            df_loc_src = df_results[['version_date', 'province', src]]
            df_loc_src.rename({src: 'reference'}, axis=1, inplace=True)
            df_loc = df_loc.merge(df_loc_src, on=['province', 'version_date'], how='left')
            list_df.append(df_loc)
        except KeyError:
            print(f'skipping {src}_{mod}')
    df = pd.concat(list_df)
    df.to_csv('compare_results.csv', index=False)


if __name__ == '__main__':
    tunnel_server = setup_tunnel()
    tunnel_server.start()
    local_port = tunnel_server.local_bind_port
    pixie_engine = create_pixie_engine(local_port=local_port)
    join_all_inputs(db_engine=pixie_engine)
    join_datasets(db_engine=pixie_engine)
    df = pd.read_csv('../data/viz_data/merge_results.csv')
    append_new_data(value_date='2022-10-01')
    comparison_forecast_results()
    pass
