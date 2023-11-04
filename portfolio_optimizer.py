import numpy as np
import pandas as pd
import glog
import json
import riskfolio as rp
from pypfopt.efficient_frontier import EfficientFrontier

from Config import optimizer_config
from Utils import path_wrapper
from plotter import plot_asset_weights, plot_asset_returns, plot_portfolio_returns


class BaseOptimizer(object):
    """The Base class for optimizer, will transform the data,  provide functions for saving the results locally,
    and integrate plot functions.

    Attributes
    ----------
    name : str
        The name of the class.
    df_return : pd.DataFrame
        A dataframe contains assets return time series.
    assets_return : np.array
        An array includes the mean return of each asset.
    assets_cov : np.array
        The covariance matrix of assets returns.
    r : float
        The risk-free rate.
    weights_vector : np.array
        An array contains allocation weights for each asset.
    asset_weights : dict
        The optimized allocation weights in dictionary format.

    Methods
    -------
    run()
        Main function to run the optimizer, will raise NotImplementedError if not implement in child class.
    save_asset_weights(label: str)
        Save asset weights in dictionary format locally.
    plot()
        Plot all the related charts and save them locally.
    """
    def __init__(self, df_return):
        self.name = self.__class__.__name__
        self.df_return = df_return
        self.assets_return = df_return.mean().values
        self.assets_cov = df_return.cov().values
        self.r = 0
        self.weights_vector = np.array([])
        self.asset_weights = {}

        self.df_return.index = pd.to_datetime(self.df_return.index)
        glog.info(f"Successfully initialize {self.name}")

    def run(self):
        raise NotImplementedError("Optimizer must implement main function run")

    def save_asset_weights(self, label: str) -> None:
        dump_dir = path_wrapper(optimizer_config['result_dump_dir'])
        file_path = f"{dump_dir}/{label}_weights.json"
        glog.info(f"Save {label} asset weights to {file_path}")
        with open(file_path, 'w') as json_file:
            json.dump(self.asset_weights, json_file)

    def plot(self):
        fig_dump_dir = path_wrapper(optimizer_config['fig_dump_dir'])

        fig_asset_weights = plot_asset_weights(self.df_return, self.weights_vector, self.name)
        fig_asset_weights.savefig(f"{fig_dump_dir}/asset_weights_pie_{self.name}.png")
        fig_asset_return = plot_asset_returns(self.df_return, self.weights_vector, self.name)
        fig_asset_return.savefig(f"{fig_dump_dir}/asset_return_{self.name}.png")
        fig_portfolio_returns = plot_portfolio_returns(self.df_return, self.weights_vector, self.name)
        fig_portfolio_returns.savefig(f"{fig_dump_dir}/portfolio_return_{self.name}.png")
        # plt.show()


class MarkowitzMeanVarianceOptimizer(BaseOptimizer):
    """The MarkowitzMeanVarianceOptimizer which inherits BaseOptimizer, will calculate the optimal
    allocation weights based on Markowitz Mean Variance Framework.

    Methods
    -------
    run()
        Main function to run the MarkowitzMeanVarianceOptimizer.
    """

    def __init__(self, df_return):
        self.lamda = 500
        super(MarkowitzMeanVarianceOptimizer, self).__init__(df_return)

    def run(self):
        ef = EfficientFrontier(self.assets_return, self.assets_cov, weight_bounds=[-1, 1])
        ef.max_quadratic_utility(risk_aversion=self.lamda, market_neutral=False)
        cleaned_weights = ef.clean_weights()
        asset_weights_markowitz = pd.DataFrame(cleaned_weights, index=['weights']).values[0]
        self.weights_vector = asset_weights_markowitz

        for idx, symbol in enumerate(self.df_return.columns):
            self.asset_weights[symbol] = asset_weights_markowitz[idx]
        self.save_asset_weights(self.name)
        self.plot()
        return asset_weights_markowitz


class RiskParityOptimizer(BaseOptimizer):
    """The RiskParityOptimizer which inherits BaseOptimizer, will calculate the optimal
    allocation weights based on Risk-Parity Theory.

    Methods
    -------
    run()
        Main function to run the RiskParityOptimizer.
    """

    def __init__(self, df_return):
        super(RiskParityOptimizer, self).__init__(df_return)

    def run(self):
        # Building the portfolio object
        port = rp.Portfolio(returns=self.df_return)

        # Calculating optimal portfolio
        port.assets_stats(method_mu='hist', method_cov='hist', d=0.94)
        w_rp = port.rp_optimization(model='Classic', rm='MV', rf=self.r, b=None, hist=True)

        asset_weights_rp = w_rp.squeeze().values
        self.weights_vector = asset_weights_rp

        for idx, symbol in enumerate(self.df_return.columns):
            self.asset_weights[symbol] = asset_weights_rp[idx]
        self.save_asset_weights(self.name)
        self.plot()
        return asset_weights_rp


if __name__ == '__main__':
    df_return = pd.read_csv(f"./data/perp_return.csv", index_col=0)

    mv_optimizer = MarkowitzMeanVarianceOptimizer(df_return)
    asset_weights_mv = mv_optimizer.run()

    mv_rp = RiskParityOptimizer(df_return)
    asset_weights_rp = mv_rp.run()
