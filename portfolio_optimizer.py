import numpy as np
import pandas as pd
import glog
import json
import riskfolio as rp
from pypfopt.efficient_frontier import EfficientFrontier

from Config import optimizer_config
from Utils import path_wrapper


class BaseOptimizer(object):
    def __init__(self, df_return):
        self.name = self.__class__.__name__
        self.df_return = df_return
        self.assets_return = df_return.mean().values
        self.assets_cov = df_return.cov().values
        self.quarterly_conversion_factor = 4
        self.n_assets = df_return.shape[1]
        self.assets_ones = np.ones(self.n_assets)
        self.zero_series = pd.Series([0] * df_return.shape[0], index=df_return.index)
        self.T = self.df_return.shape[1]
        self.r = 0
        self.asset_weights = {}
        glog.info(f"Successfully initialize {self.name}")

    def run(self):
        raise NotImplementedError("Optimizer must implement main function run")

    def save_asset_weights(self, label: str):
        dump_dir = path_wrapper(optimizer_config['result_dump_dir'])
        file_path = f"{dump_dir}/{label}_weights.json"
        glog.info(f"Save {label} asset weights to {file_path}")
        with open(file_path, 'w') as json_file:
            json.dump(self.asset_weights, json_file)


class MarkowitzMeanVarianceOptimizer(BaseOptimizer):
    def __init__(self, df_return):
        self.lamda = 500
        super(MarkowitzMeanVarianceOptimizer, self).__init__(df_return)

    def run(self):
        ef = EfficientFrontier(self.assets_return, self.assets_cov, weight_bounds=[-1, 1])
        ef.max_quadratic_utility(risk_aversion=self.lamda, market_neutral=False)
        cleaned_weights = ef.clean_weights()
        asset_weights_markowitz = pd.DataFrame(cleaned_weights, index=['weights']).values[0]

        for idx, symbol in enumerate(self.df_return.columns):
            self.asset_weights[symbol] = asset_weights_markowitz[idx]
        self.save_asset_weights(self.name)
        return asset_weights_markowitz


class RiskParityOptimizer(BaseOptimizer):
    def __init__(self, df_return):
        super(RiskParityOptimizer, self).__init__(df_return)

    def run(self):
        # Building the portfolio object
        port = rp.Portfolio(returns=self.df_return)

        # Calculating optimal portfolio
        port.assets_stats(method_mu='hist', method_cov='hist', d=0.94)
        w_rp = port.rp_optimization(model='Classic', rm='MV', rf=self.r, b=None, hist=True)

        asset_weights_rp = w_rp.squeeze().values

        for idx, symbol in enumerate(self.df_return.columns):
            self.asset_weights[symbol] = asset_weights_rp[idx]
        self.save_asset_weights(self.name)
        return asset_weights_rp


if __name__ == '__main__':
    df_return = pd.read_csv(f"./data/perp_return.csv", index_col=0)

    mv_optimizer = MarkowitzMeanVarianceOptimizer(df_return)
    asset_weights_mv = mv_optimizer.run()
    print(asset_weights_mv)

    mv_rp = RiskParityOptimizer(df_return)
    asset_weights_rp = mv_rp.run()
    print(asset_weights_rp)
