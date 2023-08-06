from datetime import datetime
from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas.plotting import autocorrelation_plot
from dateutil.relativedelta import relativedelta
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from math import sqrt
from price_forecast.etl import setup_tunnel, create_pixie_engine
from price_forecast.data_quality_reference import mode_dict
from price_forecast.queries_templates import reset_use_tag, query_read_data


class DataHandler:
    VALID_MODES: dict = {'csv': 'csv', 'pixie': 'price_clean_data'}

    def __init__(self, mode: str, db_engine=None):
        try:
            self.mode = self.VALID_MODES[mode]
            self.engine = db_engine
        except KeyError:
            valid_modes = ', '.join(self.VALID_MODES.keys())
            raise ValueError(f'{mode} is an invalid mode type. Valid modes are: ({valid_modes})')

    @staticmethod
    def load_csv(path: str) -> pd.DataFrame:
        df = pd.read_csv(path)
        return df

    def load_posgres(self, path: str):
        df = pd.read_sql(query_read_data(table_name=self.mode, mode=path, use_tag=True), self.engine)
        return df

    def load_data(self, path: str) -> pd.DataFrame:
        fun_dict = {'csv': DataHandler.load_csv, 'price_clean_data': self.load_posgres}
        return fun_dict[self.mode](path=path)


class Forecaster(ABC):
    VALID_PREDICTION_UNITS = ['D', 'M']
    PROVINCE_COL = 'province'
    FEATURES = ['visits', 'number_properties', 'leads']

    def __init__(self,
                 mode: str,
                 date_col_name: str,
                 input_path: str,
                 train_from: str,
                 train_to: str,
                 date_format: str = '%Y-%m-%d',
                 horizon: int = 1,
                 unit: str = 'M',
                 target: str = 'mean_unitary_price',
                 province: str = None,
                 max_date: str = None,
                 db_engine=None):
        self.model = None
        self.metadata = locals()
        self.dh = DataHandler(mode=mode, db_engine=db_engine)
        self.date_col_name = date_col_name
        self.train_from = pd.to_datetime(train_from, format=date_format)
        self.train_to = pd.to_datetime(train_to, format=date_format)
        self.horizon = horizon
        self.unit = unit
        self.target = target
        self.__train_data, self.__test_data = self.load_data(path=input_path, province=province, max_date=max_date)

    @staticmethod
    def create_param_grid(**kwargs):
        params = np.meshgrid(*kwargs.values())
        flatten_params = list()
        for i in params:
            flatten_params.append(i.flatten())
        return flatten_params

    def plot_autocorrelation(self):
        autocorrelation_plot(self.train_data[self.target])
        plt.show()

    def load_data(self, path: str, province: str = None, max_date: str = None):
        df = self.dh.load_data(path=path)
        df[self.date_col_name] = pd.to_datetime(df[self.date_col_name])
        if max_date is None:
            max_date = df[self.date_col_name].max()
        train_data = df.loc[(df[self.date_col_name] >= self.train_from) &
                            (df[self.date_col_name] < self.train_to), :]
        train_data.set_index(self.date_col_name, inplace=True)
        test_data = df.loc[(df[self.date_col_name] >= self.train_to) &
                           (df[self.date_col_name] <= max_date), :]
        test_data.set_index(self.date_col_name, inplace=True)
        if province is not None:
            train_data = train_data.loc[train_data[self.PROVINCE_COL] == province, :]
            test_data = test_data.loc[test_data[self.PROVINCE_COL] == province, :]
        if self.unit == 'M':
            agg_cols = self.FEATURES + [self.target]
            train_data = train_data.groupby([train_data.index.year, train_data.index.month])[agg_cols].mean().astype(int)
            test_data = test_data.groupby([test_data.index.year, test_data.index.month])[agg_cols].mean().astype(int)
        return train_data, test_data

    @abstractmethod
    def train_model(self, **kwargs):
        pass

    @abstractmethod
    def predict(self):
        pass

    @abstractmethod
    def save_model(self, out_path):
        pass

    @abstractmethod
    def load_model(self, out_path):
        pass

    # Properties
    @property
    def train_data(self):
        return self.__train_data

    @train_data.setter
    def train_data(self, new_df):
        new_df.sort_index(ascending=False, inplace=True)
        self.__train_data = new_df

    @property
    def test_data(self):
        return self.__test_data

    @test_data.setter
    def test_data(self, new_df):
        new_df.sort_index(ascending=False, inplace=True)
        self.__test_data = new_df

    @property
    def total_data(self):
        df = pd.concat([self.train_data, self.test_data])
        df.sort_index(ascending=True, inplace=True)
        return df


class ArimaPrice(Forecaster):
    def __init__(self,
                 mode: str,
                 train_from: str,
                 train_to: str,
                 date_col_name: str,
                 input_path: str,
                 date_format: str = '%Y-%m-%d',
                 horizon: int = 1,
                 unit: str = 'M',
                 target: str = 'mean_unitary_price',
                 province: str = None,
                 max_date: str = None,
                 db_engine=None):
        super().__init__(mode=mode, train_from=train_from,
                         train_to=train_to, date_format=date_format, date_col_name=date_col_name,
                         input_path=input_path,
                         horizon=horizon, unit=unit, target=target, province=province, max_date=max_date,
                         db_engine=db_engine)

    def run_backtesting(self, autoregression, diff_order, moving_average_order):
        """
        Executes backtesting
        :param autoregression: Lag in months for autoregression.
        :param diff_order: Difference of order.
        :param moving_average_order: Order of moving average.
        :return: Train and test data for later use, mean squared error
        """
        complete_data = list(self.train_data[self.target].values.copy())
        prediction = list()
        for i in range(self.test_data.shape[0]):
            model = ARIMA(complete_data, order=(autoregression,
                                                diff_order,
                                                moving_average_order), enforce_stationarity=False)
            model_fit = model.fit()
            pred = model_fit.forecast()
            prediction.append(pred)
            complete_data.append(self.test_data[self.target].iloc[i])
        smse = sqrt(mean_squared_error(prediction, self.test_data[self.target].values))
        return complete_data, smse

    def instance_output_data(self):
        """Instance DF to generate output."""
        out_data = self.total_data.copy()
        # set all dates to the first day of the month.
        date_col = [pd.to_datetime(f'{item[0]}-{item[1]}-01', format='%Y-%m-%d') for item in out_data.index]
        out_data['datetime'] = date_col
        out_data.set_index('datetime', inplace=True)
        out_data = out_data[[self.target, 'number_properties']]
        out_data['forecast'] = np.nan
        out_data['forecast_down'] = np.nan
        out_data['forecast_up'] = np.nan
        max_date = max(date_col)
        out_data.loc[max_date, 'forecast'] = out_data.loc[max_date, self.target]
        out_data.loc[max_date, 'forecast_down'] = out_data.loc[max_date, self.target]
        out_data.loc[max_date, 'forecast_up'] = out_data.loc[max_date, self.target]
        return out_data

    def prepare_output_data(self, arima_forecast, arima_ci):
        """
        Instance historical data and append forecast with confidence interval.
        :param arima_forecast:
        :param arima_ci: confidence interval array.
        :return:
        """
        total_data = self.instance_output_data()
        new_date_col = [max(total_data.index) + relativedelta(months=item + 1) for item in range(self.horizon)]
        results = pd.DataFrame({'datetime': new_date_col, 'forecast': arima_forecast})
        int_df = pd.DataFrame(arima_ci, columns=['forecast_down', 'forecast_up'])
        int_df['datetime'] = new_date_col
        results = results.merge(int_df, how='left', on='datetime')
        results[self.target] = np.nan
        results['number_properties'] = np.nan
        results.set_index('datetime', inplace=True)
        total_data = pd.concat([total_data, results])
        return total_data

    def train_model(self, **kwargs):
        results_dict = list()
        params = Forecaster.create_param_grid(**kwargs)
        # Run search grid.
        for i_ar, j_or, k_ma in zip(*params):
            local_result = {'autoregression': i_ar, 'order': j_or, 'moving_avg': k_ma}
            complete_data, smse = self.run_backtesting(i_ar, j_or, k_ma)
            local_result['error'] = smse
            results_dict.append(local_result)
        results = pd.DataFrame(results_dict)
        results.sort_values('error', ascending=True, inplace=True)
        # Get results with optimal.
        optimal_param = results.iloc[0, :]
        mse = optimal_param.error
        model = ARIMA(complete_data,
                      order=(optimal_param['autoregression'],
                             optimal_param['order'],
                             optimal_param['moving_avg']))
        self.metadata['optimal_model_params'] = optimal_param
        self.metadata['mse'] = mse
        print(mse)
        self.model = model.fit()

    def predict(self, arima_ci: float = 0.05, plot: bool = False):
        # Compute prediction and interval confidence.
        forecast = self.model.get_forecast(self.horizon)
        result = forecast.predicted_mean
        yhat_conf_int = forecast.conf_int(alpha=arima_ci)
        total_data = self.prepare_output_data(arima_forecast=result, arima_ci=yhat_conf_int)
        total_data['error'] = self.metadata['mse']
        if plot:
            total_data.plot()
            plt.title(f'Price forecast for {self.metadata["province"]}')
            plt.show()
        return total_data

    def save_model(self, out_path):
        pass

    def load_model(self, out_path):
        pass


class RFPrice(Forecaster):
    def __init__(self,
                 mode: str,
                 train_from: str,
                 train_to: str,
                 date_col_name: str,
                 input_path: str,
                 date_format: str = '%Y-%m-%d',
                 horizon: int = 1,
                 unit: str = 'M',
                 target: str = 'mean_unitary_price',
                 province: str = None,
                 max_date: str = None, db_engine=None):
        super().__init__(mode=mode, train_from=train_from,
                         train_to=train_to, date_format=date_format, date_col_name=date_col_name,
                         input_path=input_path,
                         horizon=horizon, unit=unit, target=target, province=province, max_date=max_date,
                         db_engine=db_engine)

    def apply_feature_engineering(self, df, lags: list, features: list):
        df_features = df.loc[:, features]
        df_target = df.loc[:, self.target].shift()
        df_features = df_features.merge(df_target, how='left', left_index=True, right_index=True)
        df_features.rename({self.target: self.target+'_1'}, inplace=True)
        for lag in lags:
            df_lcl = df.loc[:, features+[self.target]].copy()
            df_lcl = df_lcl.shift(lag)
            df_lcl.rename({i: i + '_' + str(lag) for i in df_lcl.columns}, axis=1, inplace=True)
            df_features = df_features.merge(df_lcl, how='left', left_index=True, right_index=True)
        df_features.dropna(inplace=True)
        target = df.loc[:, self.target]
        target = target.loc[target.index >= df_features.index.min(), :]
        return df_features, target

    def apply_feature_engineering_pred(self, df, lags: list, features: list):
        # add one row
        month_idx = df.index.max()[1] + 1
        if month_idx/12 > 1:
            month_idx = month_idx % 12
            year_idx = df.index.max()[0] + 1
        else:
            year_idx = df.index.max()[0]
        df.loc[(year_idx, month_idx), :] = np.nan
        df_features = df.loc[:, features].copy()
        df_target = df.loc[:, self.target].shift()
        df_features.rename({self.target: self.target + '_1'}, inplace=True)
        df_features = df_features.merge(df_target, how='left', left_index=True, right_index=True)
        for lag in lags:
            df_lcl = df.loc[:, features+[self.target]].copy()
            df_lcl = df_lcl.shift(lag)
            df_lcl.rename({i: i + '_' + str(lag) for i in df_lcl.columns}, axis=1, inplace=True)
            df_features = df_features.merge(df_lcl, how='left', left_index=True, right_index=True)
        df_features.ffill(inplace=True)
        return df_features

    def run_backtesting(self, **kwargs):
        """
        Executes backtesting
        :param autoregression: Lag in months for autoregression.
        :param diff_order: Difference of order.
        :param moving_average_order: Order of moving average.
        :return: Train and test data for later use, mean squared error
        """
        df_features, df_target = self.apply_feature_engineering(df=self.train_data.copy(),
                                                                lags=[3, 6],
                                                                features=['visits', 'leads'])
        df_features_test, df_target_test = self.apply_feature_engineering(df=self.total_data.copy(),
                                                                          lags=[3, 6],
                                                                          features=['visits', 'leads'])
        df_features_test = df_features_test.loc[df_features_test.index >= self.test_data.index.min(), :]
        df_target_test = df_target_test.loc[df_target_test.index >= self.test_data.index.min(), :]
        prediction = list()
        for idx, obs in df_features_test.iterrows():
            model = RandomForestRegressor(**kwargs)
            model.fit(df_features, df_target)
            pred = model.predict([obs])
            prediction.append(pred)
            df_features = df_features.append(obs)
            df_target = df_target.append(df_target_test.loc[df_target_test.index == idx, :])
        smse = sqrt(mean_squared_error(prediction, self.test_data[self.target].values))
        return df_features, smse

    def instance_output_data(self):
        """Instance DF to generate output."""
        out_data = self.total_data.copy()
        # set all dates to the first day of the month.
        date_col = [pd.to_datetime(f'{item[0]}-{item[1]}-01', format='%Y-%m-%d') for item in out_data.index]
        out_data['datetime'] = date_col
        out_data.set_index('datetime', inplace=True)
        out_data = out_data[[self.target, 'number_properties']]
        out_data['forecast'] = np.nan
        out_data['forecast_down'] = np.nan
        out_data['forecast_up'] = np.nan
        max_date = max(date_col)
        out_data.loc[max_date, 'forecast'] = out_data.loc[max_date, self.target]
        out_data.loc[max_date, 'forecast_down'] = out_data.loc[max_date, self.target]
        out_data.loc[max_date, 'forecast_up'] = out_data.loc[max_date, self.target]
        return out_data

    def prepare_output_data(self, arima_forecast, arima_ci):
        """
        Instance historical data and append forecast with confidence interval.
        :param arima_forecast:
        :param arima_ci: confidence interval array.
        :return:
        """
        total_data = self.instance_output_data()
        new_date_col = [max(total_data.index) + relativedelta(months=item + 1) for item in range(self.horizon)]
        results = pd.DataFrame({'datetime': new_date_col, 'forecast': arima_forecast})
        int_df = pd.DataFrame(arima_ci, columns=['forecast_down', 'forecast_up'])
        int_df['datetime'] = new_date_col
        results = results.merge(int_df, how='left', on='datetime')
        results[self.target] = np.nan
        results['number_properties'] = np.nan
        results.set_index('datetime', inplace=True)
        total_data = pd.concat([total_data, results])
        return total_data

    def train_model(self, **kwargs):
        results_dict = list()
        params = Forecaster.create_param_grid(**kwargs)
        # Run search grid.
        for b, md, mf, msl, mss, ne in zip(*params):
            local_result = {'bootstrap': b, 'max_depth': md, 'max_features': mf,
                            'min_samples_leaf': msl, 'min_samples_split': mss, 'n_estimators': ne}
            complete_data, smse = self.run_backtesting(**local_result)
            local_result['error'] = smse
            results_dict.append(local_result)
        results = pd.DataFrame(results_dict)
        results.sort_values('error', ascending=True, inplace=True)
        # Get results with optimal.
        optimal_param = results.iloc[0, :]
        mse = optimal_param.error
        model = RandomForestRegressor(**optimal_param.drop('error'))
        df_features, df_target = self.apply_feature_engineering(df=self.total_data.copy(),
                                                                lags=[3, 6],
                                                                features=['visits', 'leads'])
        model.fit(df_features, df_target)
        self.metadata['optimal_model_params'] = optimal_param
        self.metadata['mse'] = mse
        print(mse)
        self.model = model

    def predict(self, arima_ci: float = 0.05, plot: bool = False):
        # Compute prediction and interval confidence.
        results = list()
        yhat_conf_int = list()
        ftr = self.total_data.copy()
        all_target = list(ftr[self.target].values)
        for _ in range(self.horizon):
            ftr = self.apply_feature_engineering_pred(df=ftr, lags=[3, 6], features=['visits', 'leads'])
            result = self.model.predict([ftr.iloc[-1, :]])
            all_target.append(result[0])
            ftr = ftr[['visits', 'leads']]
            ftr.loc[:, self.target] = all_target
            results.append(result[0])
            yhat_conf_int.append((result[0], result[0]))
        total_data = self.prepare_output_data(arima_forecast=results, arima_ci=yhat_conf_int)
        total_data['error'] = self.metadata['mse']
        if plot:
            total_data.plot()
            plt.title(f'Price forecast for {self.metadata["province"]}')
            plt.show()
        return total_data

    def save_model(self, out_path):
        pass

    def load_model(self, out_path):
        pass


class NNPrice(Forecaster):
    def __init__(self,
                 mode: str,
                 train_from: str,
                 train_to: str,
                 date_col_name: str,
                 input_path: str,
                 date_format: str = '%Y-%m-%d',
                 horizon: int = 1,
                 unit: str = 'M',
                 target: str = 'mean_unitary_price',
                 province: str = None,
                 max_date: str = None, db_engine=None):
        super().__init__(mode=mode, train_from=train_from,
                         train_to=train_to, date_format=date_format, date_col_name=date_col_name,
                         input_path=input_path, db_engine=db_engine,
                         horizon=horizon, unit=unit, target=target, province=province, max_date=max_date)
        self.scaler = StandardScaler()
        self.scaler.fit(self.train_data)

    def apply_feature_engineering(self, df, lags: list, features: list):
        df_features = df.loc[:, features]
        df_target = df.loc[:, self.target].shift()
        df_features = df_features.merge(df_target, how='left', left_index=True, right_index=True)
        df_features.rename({self.target: self.target+'_1'}, inplace=True)
        for lag in lags:
            df_lcl = df.loc[:, features+[self.target]].copy()
            df_lcl = df_lcl.shift(lag)
            df_lcl.rename({i: i + '_' + str(lag) for i in df_lcl.columns}, axis=1, inplace=True)
            df_features = df_features.merge(df_lcl, how='left', left_index=True, right_index=True)
        df_features.dropna(inplace=True)
        target = df.loc[:, self.target]
        target = target.loc[target.index >= df_features.index.min(), :]
        return df_features, target

    def apply_feature_engineering_pred(self, df, lags: list, features: list):
        # add one row
        month_idx = df.index.max()[1] + 1
        if month_idx/12 > 1:
            month_idx = month_idx % 12
            year_idx = df.index.max()[0] + 1
        else:
            year_idx = df.index.max()[0]
        df.loc[(year_idx, month_idx), :] = np.nan
        df_features = df.loc[:, features].copy()
        df_target = df.loc[:, self.target].shift()
        df_features.rename({self.target: self.target + '_1'}, inplace=True)
        df_features = df_features.merge(df_target, how='left', left_index=True, right_index=True)
        for lag in lags:
            df_lcl = df.loc[:, features+[self.target]].copy()
            df_lcl = df_lcl.shift(lag)
            df_lcl.rename({i: i + '_' + str(lag) for i in df_lcl.columns}, axis=1, inplace=True)
            df_features = df_features.merge(df_lcl, how='left', left_index=True, right_index=True)
        df_features.ffill(inplace=True)
        return df_features

    def instance_tf_model(self, n_past):
        """

        :param n_past:
        :return:
        """
        _, n_features = self.train_data.shape
        n_neurons = 100
        encoder_inputs = tf.keras.layers.Input(shape=(n_past, n_features))
        encoder_l1 = tf.keras.layers.LSTM(n_neurons, return_state=True)
        encoder_outputs1 = encoder_l1(encoder_inputs)
        encoder_states1 = encoder_outputs1[1:]
        decoder_inputs = tf.keras.layers.RepeatVector(self.horizon)(encoder_outputs1[0])
        decoder_l1 = tf.keras.layers.LSTM(n_neurons, return_sequences=True)(decoder_inputs, initial_state=encoder_states1)
        decoder_outputs1 = tf.keras.layers.TimeDistributed(tf.keras.layers.Dense(n_features))(decoder_l1)
        model = tf.keras.models.Model(encoder_inputs, decoder_outputs1)
        model.compile(optimizer=tf.keras.optimizers.Adam(), loss=tf.keras.losses.Huber())
        self.model = model

    def split_series(self, df: pd.DataFrame, n_past: int, n_future: int):
        """
        Scale and normalize dataset.
        :param df: Raw pandas DataFrame
        :param n_past: number of past observations
        :param n_future: number of future observations
        :return: split of windowed
        """
        series = self.scaler.transform(df)
        x, y = list(), list()
        for window_start in range(len(series)):
            past_end = window_start + n_past
            future_end = past_end + n_future
            if future_end > len(series):
                break
            # slicing the past and future parts of the window
            past, future = series[window_start:past_end, :], series[past_end:future_end, :]
            x.append(past)
            y.append(future)
        return np.array(x), np.array(y)

    def instance_output_data(self):
        """Instance DF to generate output."""
        out_data = self.total_data.copy()
        # set all dates to the first day of the month.
        date_col = [pd.to_datetime(f'{item[0]}-{item[1]}-01', format='%Y-%m-%d') for item in out_data.index]
        out_data['datetime'] = date_col
        out_data.set_index('datetime', inplace=True)
        out_data = out_data[[self.target, 'number_properties']]
        out_data['forecast'] = np.nan
        out_data['forecast_down'] = np.nan
        out_data['forecast_up'] = np.nan
        max_date = max(date_col)
        out_data.loc[max_date, 'forecast'] = out_data.loc[max_date, self.target]
        out_data.loc[max_date, 'forecast_down'] = out_data.loc[max_date, self.target]
        out_data.loc[max_date, 'forecast_up'] = out_data.loc[max_date, self.target]
        return out_data

    def prepare_output_data(self, forecast_result, tuple_ci):
        """
        Instance historical data and append forecast with confidence interval.
        :param forecast_result:
        :param tuple_ci: confidence interval array.
        :return:
        """
        total_data = self.instance_output_data()
        new_date_col = [max(total_data.index) + relativedelta(months=item + 1) for item in range(self.horizon)]
        results = pd.DataFrame({'datetime': new_date_col, 'forecast': forecast_result})
        int_df = pd.DataFrame(tuple_ci, columns=['forecast_down', 'forecast_up'])
        int_df['datetime'] = new_date_col
        results = results.merge(int_df, how='left', on='datetime')
        results[self.target] = np.nan
        results['number_properties'] = np.nan
        results.set_index('datetime', inplace=True)
        total_data = pd.concat([total_data, results])
        return total_data

    def train_model(self, **kwargs):
        months_back = 18
        test_months_back = self.train_to-relativedelta(months=months_back)
        test_data = self.total_data.loc[self.total_data.index >= (test_months_back.year, test_months_back.month), :]
        self.instance_tf_model(n_past=months_back)
        reduce_lr = tf.keras.callbacks.LearningRateScheduler(lambda x: 1e-3 * 0.90 ** x)
        # Prepare data
        x_train, y_train = self.split_series(df=self.train_data, n_past=months_back, n_future=self.horizon)
        x_test, y_test = self.split_series(df=test_data, n_past=months_back, n_future=self.horizon)
        self.model.fit(x_train, y_train, epochs=100, validation_data=(x_test, y_test), batch_size=12,
                       verbose=0, callbacks=[reduce_lr])
        # Run search grid.
        pred = self.model.predict(x_test)
        array_data = self.scaler.inverse_transform(pred)
        prediction = pd.DataFrame(array_data[-1], columns=self.train_data.columns)
        mse_error = sqrt(mean_squared_error(prediction[self.target], list(self.test_data[self.target])))
        print(mse_error)
        self.metadata['mse'] = mse_error

    def predict(self, arima_ci: float = 0.05, plot: bool = False):
        months_back = 18
        test_months_back = self.train_to - relativedelta(months=months_back)
        test_data = self.total_data.loc[self.total_data.index >= (test_months_back.year, test_months_back.month), :]
        x_test, _ = self.split_series(df=test_data, n_past=months_back, n_future=self.horizon)
        pred = self.model.predict(x_test)
        array_data = self.scaler.inverse_transform(pred)
        prediction = pd.DataFrame(array_data[-1], columns=self.train_data.columns)
        array_list = list(prediction[self.target])
        yhat_conf_int = list(zip(array_list, array_list))
        total_data = self.prepare_output_data(forecast_result=prediction[self.target], tuple_ci=yhat_conf_int)
        total_data['error'] = self.metadata['mse']
        if plot:
            print('Nothing to do')
        return total_data

    def save_model(self, out_path):
        pass

    def load_model(self, out_path):
        pass


run_dict = {'arima': {'model': ArimaPrice},
            'random_forest': {'model': RFPrice},
            'nn': {'model': NNPrice}}


def run_forecast(model_name: str,
                 input_path: str,
                 province_list: list,
                 search_grid: dict,
                 train_from: str, operation_type: str, db_engine,
                 train_to: str, max_date: str, mode: str = 'pixie', horizon: int = 12, debug: bool = False):
    """
    Call forecast algorithm using parameters
    :param max_date: last month to be used in the test set. Test set goes from train_to+1 to max_date, both inclusive.
    :param model_name: Model key as in run_dict: arima, random_forest, nn.
    :param input_path: Name of the forecast: key from mode_dict (from data_quality_reference)
    :param province_list: List of provinces to be forecasted.
    :param search_grid: Dictionary containing the search space
    :param operation_type: rent or buy.
    :param db_engine: Database Engine
    :param train_from: Start date for backtesting.
    :param train_to: End date for backtesting (not inclusive in training).
    :param mode: Mode of loading data (csv, s3, etc.). pixie gets data from Datavenues.
    :param horizon: Number of months to be forecasted.
    :param debug: Do nothing
    :return: Export forecast with format model_name.csv. It contains history with the forecast and interval of
    confidence.
    """
    t0 = datetime.now()
    list_res = list()
    input_model = {'mode': mode, 'train_from': train_from, 'train_to': train_to, 'date_col_name': 'version_date',
                   'input_path': input_path, 'horizon': horizon, 'max_date': max_date, 'db_engine': db_engine}
    if 'rent' in operation_type:
        input_model['target'] = 'mean_price'
    else:
        input_model['target'] = 'mean_unitary_price'
    for province in province_list:
        print(province)
        input_model.update({'province': province})
        fcst = run_dict[model_name]['model'](**input_model)
        try:
            fcst.train_model(**search_grid)
            results = fcst.predict(plot=False)
            results['province'] = province
            list_res.append(results)
        except Exception as e:
            print(f'{province} failed with error {e}')
    list_res = pd.concat(list_res)
    list_res['model'] = model_name
    list_res['target_name'] = input_model['target']
    list_res.rename({input_model['target']: 'target'}, axis=1, inplace=True)
    list_res['forecast_date'] = datetime.strftime(datetime.today(), '%Y-%m-%d')
    list_res['tag_use'] = True
    list_res['extraction_type'] = input_path
    if debug:
        print(f'{model_name} took {datetime.now()-t0}')
    else:
        list_res.to_sql('price_forecasts', db_engine, if_exists='append')


def run_all_forecasts(credentials: dict, train_from, train_to, max_date, debug: bool = False):
    """
    Run all the forecast models defined in models_dict. This function contains the setup of grid search.
    :param credentials: Credentials to connect to Datavenues.
    :param train_from: Training set is defined as (train_from, train_to). format '%Y-%m-%d'
    :param train_to: Last day of training data (This month is not inclusive).
    :param max_date: Last day that defines test set. test_set = (train_to, max_date) both inclusive.
    :param debug:
    :return: Appends forecasts in table price_forecasts in datavenues.
    """
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
    if not debug:
        # This deprecates the last forecast
        q = reset_use_tag('price_forecasts')
        pixie_engine.execute(q)
    for data_source, _ in mode_dict.items():
        print(data_source)
        if (data_source != 'demand_flat_sell') and debug:
            continue
        path = data_source
        op_type = data_source
        if debug:
            provinces = ['Barcelona', 'Madrid']
        else:
            df = pd.read_sql(query_read_data(table_name='price_clean_data', mode=data_source, use_tag=True),
                             pixie_engine)
            provinces = df.province.unique()
        # Arima
        search_grid = {'autoregression': [2, 3, 4, 5], 'order': [1, 2], 'm_avg': [0, 1, 2]}
        run_forecast(model_name='arima', input_path=path, province_list=provinces,
                     search_grid=search_grid, train_from=train_from, train_to=train_to,
                     operation_type=op_type, max_date=max_date,
                     db_engine=pixie_engine, horizon=3, debug=debug)
        # NN
        run_forecast(model_name='nn', input_path=path, province_list=provinces,
                     search_grid=search_grid, train_from=train_from, train_to=train_to,
                     operation_type=op_type, max_date=max_date,
                     horizon=3, db_engine=pixie_engine, debug=debug)
        # RF
        search_grid = {'bootstrap': [False],
                       'max_depth': [10, 30, 50],
                       'max_features': ['auto'],
                       'min_samples_leaf': [1],
                       'min_samples_split': [2],
                       'n_estimators': [100, 200, 400]}
        run_forecast(model_name='random_forest', input_path=path, province_list=provinces,
                     search_grid=search_grid, train_from=train_from, train_to=train_to,
                     operation_type=op_type, max_date=max_date,
                     db_engine=pixie_engine, horizon=3, debug=debug)
    tunnel_server.stop()


if __name__ == '__main__':
    pass
