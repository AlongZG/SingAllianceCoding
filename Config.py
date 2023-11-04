import pandas as pd

# fetching data config
data_config = {
    "binance_api_url": "https://fapi.binance.com/fapi/v1/klines",  # future data url
    "data_freq": "1h",                                             # data resolution
    "symbol_list": ["BTC", "ETH", "LTC"],                          # asset symbols
    "data_fetch_max_trial": 5,                                     # maximum trials for fetching data
    "s_2_ms_convert_multiplier": 1e3,                              # multiplier to convert s to ms
    "data_dump_dir": "./data"                                      # dir for saving data locally
}

# optimizer config
optimizer_config = {
    "result_dump_dir": "./result",       # dir for saving results locally
    "fig_dump_dir": "./picture"          # dir for saving figs locally
}

# times
start_time = pd.to_datetime("2023-09-01")   # the analysis start time
end_time = pd.to_datetime("2023-09-02")     # the analysis end time
