import pandas as pd
import riskfolio as rp
import matplotlib.pyplot as plt
import numpy as np


def plot_asset_weights(df_return: pd.DataFrame, asset_weights: np.array, label: str = ''):
    asset_weights = pd.DataFrame(asset_weights, index=df_return.columns)

    fig = plt.figure(figsize=[10, 10], dpi=100)
    rp.plot_pie(w=asset_weights,
                title=label,
                others=0.05,
                nrow=25,
                cmap="tab20",
                height=6,
                width=10,
                ax=None)
    return fig


def plot_asset_returns(df_return: pd.DataFrame, asset_weights: np.array, label: str = ''):
    fig = plt.figure(figsize=[12, 5], dpi=200)
    plt.title(f"{label} Asset Returns")
    n_assets = df_return.shape[1]
    zero_series = pd.Series([0] * df_return.shape[0], index=df_return.index)

    for index, col in enumerate(df_return.columns):
        plt.plot(df_return[col] * asset_weights[index] / n_assets, label=col)
    plt.plot(zero_series, label='zero', color='gray', linestyle='--')

    plt.legend()
    return fig


def plot_portfolio_returns(df_return, asset_weights, label=''):
    fig, ax1 = plt.subplots(figsize=[12, 5], dpi=200)
    plt.title(f"{label} Portfolio Returns & Cumulative Returns")
    zero_series = pd.Series([0] * df_return.shape[0], index=df_return.index)

    plt.plot(zero_series, label='zero', color='gray', linestyle='--', linewidth=2)
    ax2 = ax1.twinx()

    ax1.plot((df_return * asset_weights).mean(axis=1), label='returns', color='orange')
    ax1.set_ylabel('returns')
    ax1.legend()

    ax2.plot(((df_return * asset_weights).mean(axis=1) + 1).cumprod(), label='cumulative_returns')
    ax2.set_ylabel('cumulative_returns')
    ax2.legend()
    return fig


def analyze_performance(assets_return, asset_weights, assets_cov):
    annualizing_factor = 365
    return_portfolio = (assets_return @ asset_weights) * annualizing_factor
    volatility_portfolio = np.sqrt((asset_weights @ assets_cov @ asset_weights) * annualizing_factor)
    sharpe_portfolio = return_portfolio / volatility_portfolio
    df_performance = pd.DataFrame([[return_portfolio, volatility_portfolio, sharpe_portfolio]],
                                  columns=['Annually Return', 'Annually Volatility', 'Sharpe Ratio'])
    return df_performance


def plot_asset_weights_table(asset_weights_list: list, label_list: list):
    df_asset_weights = pd.DataFrame(asset_weights_list, index=label_list).T
    print(f"------Asset Weights Table------\n {df_asset_weights}", flush=True)
    return df_asset_weights
