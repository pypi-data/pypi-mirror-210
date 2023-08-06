# Pixie Price Forecast
This repository's main aim is to get an overview of the price tendency throughout the next few months.
It is published and distributed as a python package and it consists of the following steps:

* Daily extraction of aggregated data.
* Data Cleansing procedure.
* Price Forecast.
* Creation of table suited for visualization.

## Install package and requirements
To begin with, please install all the python modules required to run the scripts.
It is as simple as to run the following in your virtual environment.

```{batch}
pip install pixie-price-forecast
```

## Notes on Credential
This script follow the strictest guidelines to not expose any private or confidential information.
As for that, it is necessary to provide a dictionary with credentials to connect to the DB via SSH.
It is compulsory for the dictionary to have the following structure:

```{python}
credentials = {
        'ssh_user': 'ssh user',
        'ssh_pass': 'ssh password',
        'ssh_host': 'ssh host',
        'ssh_port': 'ssh port',
        'user': 'Database user',
        'password': 'Database password',
        'host': 'Database host',
        'port': 'Database port',
        'db_name': 'Name of the Database'
    }
```

We strongly advise not to expose the credentials by hard-coding it in files or script. We recommend to use alternatives 
such as Github's secrets or Databrick's secrets.

In the rest of the document we can whenever we refer to the credentials' dictionary it is a reference to the definition above.

## Running Raw Data ETL
The following code appends data corresponding to the data range '2030-01-01' - '2050-12-31' to the existing table `price_raw_data`:

```{python}
from price_forecast.etl import export_aggregated_data

update_raw_data(start_date='2030-01-01', end_date='2050-12-31', 
                credentials=credentials, first_step=1, last_step=12)
```

Please note that the date format is `'%Y-%m-%d'`.

The parameters `first_step` and `last_step` correspond the kind of extraction. The following list correspond to all the available modes with their encoding:

* 1 : demand_flat_rent
* 2 : offer_flat_rent
* 3 : professionals_flat_rent
* 4 : demand_houses_rent
* 5 : offer_houses_rent
* 6 : professionals_houses_rent
* 7 : demand_flat_sell
* 8 : offer_flat_sell
* 9 : professionals_flat_sell
* 10: demand_houses_sell
* 11: offer_houses_sell
* 12: professionals_houses_sell

Please note that `offer` corresponds to supply data.

## Running Clean Data ETL
Once every month it is important to run the ETL to clean the raw data. The results are stored in `price_clean_data` which is historized.

To run the procedure is as simple as:

```{python}
from price_forecast.etl import update_clean_data
update_clean_data(credentials=credentials)
```

In order to consume the latest clean data, we recommend the following query:

```{SQL}
SELECT
    *
FROM
    price_clean_data
WHERE
    use_tag=TRUE
```

## Forecasting Prices
As of today, it is possible to forecast the property price per province using one of the following models:

* Arima: Univariate
* Random Forest: Using leads, visits and 3-6 months lags as drivers.
* LSTM: Better suited Neural Network to learn temporal dependency

Forecast results are stored in `price_forecasts` (please notice it is plural).

You can use the following code to run all three models for all 12 modes:

```{python}
from price_forecast.forecaster import run_all_forecasts
run_all_forecasts(credentials=dict_credentials, train_from='2030-01-01', train_to='2050-09-31', max_date='2050-11-30')
```

This code will train the models using clean data, per province from january 2030 to september 2050, and tests the results from october to november 2050.
Then, it makes prediction for the next 3 months and store it in the table.

The target table is historized. In order to consume the latest results for a given province ('Barcelona' in the example) and a given mode (e.g. Supply data for sales of flats).

```{SQL}
SELECT
    *
FROM
    price_forecasts
WHERE
    use_tag=TRUE AND province='Barcelona' AND mode='offer_flat_sell'
```

## Exporting Data for Visualization
The data model is not suited to provide data to Tableau in an convenient fashion. That is why it is necessary to export them, 
in a wide format for both: clean data and forecast data

### Input Data
The visualization clean data is stored in `price_viz_inputs`. Which is historized, and can be generated as follows:

```{python}
from price_forecast.misc import join_all_inputs
from price_forecast.etl import setup_tunnel, create_pixie_engine

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
join_all_inputs(db_engine=pixie_engine)
```

To export data for Tableau run the following query:

```{SQL}
SELECT
    *
FROM
    price_viz_inputs
WHERE
    tag_use=TRUE
```

### Forecast Data
The data is stored in `price_viz_forecast` and in order to update the results run the following code:

```{python}
from price_forecast.misc import join_all_inputs
from price_forecast.etl import setup_tunnel, create_pixie_engine

tunnel_server = setup_tunnel(ssh_user=credentials['ssh_user'],
                             ssh_pass=credentials['ssh_pass'],
                             ssh_host=credentials['ssh_host'],
                             ssh_port=credentials['ssh_port'],
                             host=credentials['host'],
                             port=credentials['port'])
tunnel_server.start()
local_port = tunnel_server.local_bind_port
pixie_engine = create_pixie_engine(local_port=local_port)
join_datasets(pixie_engine)
```

The corresponding query to consume forecast data is the following:

```{SQL}
SELECT
    *
FROM
    price_viz_forecasts
WHERE
    tag_use=TRUE
```

## Next Steps
* Output validation module
* Expand data quality check

## Results
Results can be found in [this Tableau Dashboard](https://tableau.mpi-internal.com/#/site/sch-es/views/PriceForecast/GeneralView?:iid=1).

In case you do not have access, please contact [Jose Mielgo](mailto:joseangel.mielgo@adevinta.com)
