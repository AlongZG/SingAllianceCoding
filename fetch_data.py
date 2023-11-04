import pandas as pd
import requests
from requests.exceptions import HTTPError
import glog
import time
from ratelimit import rate_limited

from Config import data_config, start_time, end_time
from Utils import path_wrapper


# TODO doc string
class DataFetcher(object):
    def __init__(self):
        pass

    # 10 times/second for one IP at most
    # request the data
    @rate_limited(calls=10, period=1)
    def request_data(self, request_params: dict):
        response = requests.get(data_config["binance_api_url"], request_params)
        if response.status_code == 200:
            return response
        else:
            glog.error(f"Request failed with status code {response.status_code}， response {response.json()}")
            return None

    @staticmethod
    def format_price_data(df_data: pd.DataFrame):
        df_perp_price = df_data.copy(deep=True)
        df_perp_price.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
                                 'taker_buy_quote asset_volume', 'dummy']
        df_perp_price['time'] = pd.to_datetime((df_perp_price['timestamp'].astype('int')) * 1e6).apply(
            lambda x: x.strftime("%Y-%m-%d %H:%M:%S"))
        df_perp_price['time'] = pd.to_datetime(df_perp_price['time'])
        df_perp_price = df_perp_price.astype({'open': float, 'high': float, 'low': float, 'close': float})
        return df_perp_price

    def get_price_data(self, symbol: str):
        glog.info(f"Start to fetch data for {symbol}")
        df_data = None
        request_params = {
            "symbol": f"{symbol}USDT",
            "interval": data_config["data_freq"],
            "startTime": int(start_time.timestamp() * data_config["s_2_ms_convert_multiplier"]),
            "endTime": int(end_time.timestamp() * data_config["s_2_ms_convert_multiplier"])
        }

        for i in range(data_config["data_fetch_max_trial"]):
            try:
                res = self.request_data(request_params)
                df_data = pd.DataFrame(res.json())
                if res is not None:
                    break
            except HTTPError as e:
                glog.error(f"HTTPError! {e}, Retry after 1s.")
                time.sleep(1)

        # parse data
        df_perp_price = self.format_price_data(df_data)
        return df_perp_price

    @staticmethod
    def save_price_data(df_price: pd.DataFrame, symbol: str):
        dump_dir = path_wrapper(data_config['data_dump_dir'])
        dump_path = f"{dump_dir}/{symbol}_price.csv"
        glog.info(f"Save {symbol} price data to {dump_path}")
        df_price.to_csv(dump_path)

    @staticmethod
    def save_return_data(df_return: pd.DataFrame):
        dump_dir = path_wrapper(data_config['data_dump_dir'])
        dump_path = f"{dump_dir}/perp_return.csv"
        glog.info(f"Save perp return data to {dump_path}")
        df_return.to_csv(f"{dump_dir}/perp_return.csv")

    @staticmethod
    def load_return_data():
        data_path = f"{data_config['data_dump_dir']}/perp_return.csv"
        df_return = pd.read_csv(data_path, index_col=0)
        return df_return

    def run(self):
        return_series_list = []

        for symbol in data_config["symbol_list"]:
            df_perp_price = self.get_price_data(symbol)
            self.save_price_data(df_perp_price, symbol)
            return_series = df_perp_price['close'].pct_change()
            return_series.index = df_perp_price['time']
            return_series.dropna(inplace=True)
            return_series.name = symbol
            return_series_list.append(return_series)

        df_return = pd.concat(return_series_list, axis=1)
        self.save_return_data(df_return)


if __name__ == "__main__":
    data_fetcher = DataFetcher()
    data_fetcher.run()
