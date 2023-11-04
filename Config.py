import pandas as pd

# fetching data config
data_config = {
    "binance_api_url": "https://fapi.binance.com/fapi/v1/klines",
    "data_freq": "1h",
    "symbol_list": ["BTC", "ETH", "LTC"],
    "data_fetch_max_trial": 5,
    "s_2_ms_convert_multiplier": 1e3,
    "data_dump_dir": "./data/"
}

# times
start_time = pd.to_datetime("2023-09-01")
end_time = pd.to_datetime("2023-09-02")
