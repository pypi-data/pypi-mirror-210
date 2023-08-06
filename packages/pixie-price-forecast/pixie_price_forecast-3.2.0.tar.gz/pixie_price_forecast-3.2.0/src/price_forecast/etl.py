from sqlalchemy import create_engine
import sqlalchemy
from sshtunnel import SSHTunnelForwarder
from datetime import datetime
import pandas as pd
from price_forecast.queries_templates import *
from price_forecast.data_quality_tools import apply_data_cleansing
from price_forecast.data_quality_reference import mode_dict


def setup_tunnel(ssh_user, ssh_pass, ssh_host, ssh_port, host, port) -> SSHTunnelForwarder:
    server = SSHTunnelForwarder(
        (ssh_host, int(ssh_port)),
        ssh_username=ssh_user,
        ssh_pkey='./pixie/id_rsa',
        remote_bind_address=(host, int(port))
    )
    return server


def create_pixie_engine(local_port: int, user, password, db_name):
    connection_str = f'postgresql://{user}:{password}@127.0.0.1:' \
                     f'{local_port}/{db_name}'
    engine = create_engine(connection_str)
    return engine


def update_raw_data_feature(mode_name: str):
    df_ = pd.read_csv('../data/raw_data/' + mode_dict[mode_name]['name_export_file'])
    df_['load_date'] = datetime.today().strftime('%Y-%m-%d')
    df_['extraction_type'] = mode_name
    try:
        df_.drop('type', axis=1, inplace=True)
    except KeyError:
        print(mode_name)
    df_.to_csv('../data/raw_data/' + mode_dict[mode_name]['name_export_file'], index=False)


def update_raw_data(start_date: str, end_date: str, credentials: dict, first_step: int = 1, last_step: int = 10000):
    i = 1
    tunnel_server = setup_tunnel(ssh_user=credentials['ssh_user'],
                                 ssh_pass=credentials['ssh_pass'],
                                 ssh_host=credentials['ssh_host'],
                                 ssh_port=credentials['ssh_port'],
                                 host=credentials['host'],
                                 port=credentials['port'])
    tunnel_server.start()
    local_port = tunnel_server.local_bind_port
    pixie_engine = create_pixie_engine(local_port=local_port,
                                       user=credentials['user'],
                                       password=credentials['password'],
                                       db_name=credentials['db_name'])
    for mode, _ in mode_dict.items():
        if (i < first_step) | (i > last_step):
            print(f'skipping {i}-{mode}')
        else:
            print(f'{i}-{mode}')
            export_aggregated_data(mode_str=mode, start_date=start_date, end_date=end_date, pixie_engine=pixie_engine)
        i += 1
    tunnel_server.stop()


def export_aggregated_data(mode_str: str, start_date: str, end_date: str, pixie_engine, to_sql: bool = True):

    date_range_adv = pd.date_range(start=start_date,
                                   end=end_date,
                                   freq='D')
    df_ = list()
    for d in date_range_adv:
        str_date = d.strftime('%Y%m%d')
        table_name = f'{str_date}_advnta'
        q_obj = QueryHandler(**mode_dict[mode_str]['variables'])
        query = q_obj.create_query(table_name=table_name,
                                   var_list=['province'])
        try:
            # Storing data.
            df_loc = pd.read_sql(query, pixie_engine)
            df_loc['version_date'] = d
            df_loc['load_date'] = datetime.today()
            df_loc['extraction_type'] = mode_str
            df_.append(df_loc)
        except sqlalchemy.exc.ProgrammingError:
            # Table for this date does not exist.
            pass
        if (d.month == 1) and (d.day == 1):
            df_pre = pd.concat(df_)
            df_pre.to_csv(f'agg_prices_offer_partial_{d.year}.csv', index=False)
    df_ = pd.concat(df_)
    print(df_.shape)
    if to_sql:
        df_.to_sql('price_raw_data', pixie_engine, if_exists='append', index=False)
    else:
        df_.to_csv('../data/raw_data/test_' + mode_dict[mode_str]['name_export_file'], index=False)


def update_clean_data(credentials: dict):
    tunnel_server = setup_tunnel(ssh_user=credentials['ssh_user'],
                                 ssh_pass=credentials['ssh_pass'],
                                 ssh_host=credentials['ssh_host'],
                                 ssh_port=credentials['ssh_port'],
                                 host=credentials['host'],
                                 port=credentials['port'])
    tunnel_server.start()
    local_port = tunnel_server.local_bind_port
    pixie_engine = create_pixie_engine(local_port=local_port,
                                       user=credentials['user'],
                                       password=credentials['password'],
                                       db_name=credentials['db_name'])
    q = reset_use_tag(table_name='price_clean_data')
    pixie_engine.execute(q)
    apply_data_cleansing(db_engine=pixie_engine)
    tunnel_server.stop()


if __name__ == '__main__':
    pass
