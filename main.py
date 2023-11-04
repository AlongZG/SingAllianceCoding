import glog
import pandas as pd

from fetch_data import DataFetcher
from portfolio_optimizer import MarkowitzMeanVarianceOptimizer, RiskParityOptimizer
from plotter import analyze_performance, plot_asset_weights_table


def run_data_fetcher():
    glog.info(f"Start to run data fetcher")
    data_fetcher = DataFetcher()
    data_fetcher.run()
    df_return = data_fetcher.load_return_data()
    return df_return


def run_optimizer(df_return: pd.DataFrame):
    glog.info(f"Start to run optimizer")
    mv_optimizer = MarkowitzMeanVarianceOptimizer(df_return)
    mv_optimizer.run()

    rp_optimizer = RiskParityOptimizer(df_return)
    rp_optimizer.run()
    return mv_optimizer, rp_optimizer


def main():
    df_return = run_data_fetcher()
    mv_optimizer, rp_optimizer = run_optimizer(df_return)

    # print asset return
    print(f"------Assets Return------\n {pd.DataFrame(df_return.mean(), columns=['return']).T} \n")
    print(f"------Assets Covariance------\n {mv_optimizer.df_return.cov()} \n")

    # print asset weights
    plot_asset_weights_table([mv_optimizer.asset_weights, rp_optimizer.asset_weights],
                             [mv_optimizer.name, rp_optimizer.name])

    # print asset performance
    mv_performance = analyze_performance(
        mv_optimizer.assets_return, mv_optimizer.weights_vector, mv_optimizer.assets_cov)
    rp_performance = analyze_performance(
        rp_optimizer.assets_return, rp_optimizer.weights_vector, rp_optimizer.assets_cov)
    df_performance = pd.concat([mv_performance, rp_performance]).T
    df_performance.columns = [mv_optimizer.name, rp_optimizer.name]
    print(f"------Strategy Performance------\n {df_performance}")


if __name__ == '__main__':
    main()
