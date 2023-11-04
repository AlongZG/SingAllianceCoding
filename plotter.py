import riskfolio as rp
import matplotlib.pyplot as plt
import numpy as np

# TODO fix this

# define the functions we need
def analyze_performance(asset_weights, ):
    return_portfolio = (assets_return @ asset_weights) * quarterly_conversion_factor
    volatility_portfolio = np.sqrt((asset_weights @ assets_cov @ asset_weights) * quarterly_conversion_factor)
    sharpe_portfolio = (return_portfolio - r) / volatility_portfolio
    print(
        f"Annually Return {return_portfolio * 100:.3f}%,\n Annually Volatility {volatility_portfolio * 100:.3f}%,\n Sharpe {sharpe_portfolio:.3f}")


def plot_asset_weights(asset_weights, label=''):
    asset_weights = pd.DataFrame(asset_weights, index=df_data.columns)

    plt.figure(figsize=[6, 6], dpi=50)
    ax = rp.plot_pie(w=asset_weights,
                     title=label,
                     others=0.05,
                     nrow=25,
                     cmap="tab20",
                     height=6,
                     width=10,
                     ax=None)
    plt.show()


def plot_asset_returns(asset_weights, label=''):
    plt.figure(figsize=[18, 5], dpi=200)
    plt.title(f"{label} Asset Returns")

    for index, col in enumerate(df_data.columns):
        plt.plot(df_data[col] * asset_weights[index] / n_assets, label=col)
    plt.plot(zero_series, label='zero', color='gray', linestyle='--')
    plt.legend()
    # plt.savefig(f"./picture/{label}_asset_returns.png")
    plt.show()


def plot_portfolio_returns(asset_weights, label=''):
    fig, ax1 = plt.subplots(figsize=[18, 5], dpi=200)
    plt.title(f"{label} Portfolio Returns & Cumulative Returns")

    plt.plot(zero_series, label='zero', color='gray', linestyle='--', linewidth=2)
    ax2 = ax1.twinx()

    ax1.plot((df_data * asset_weights).mean(axis=1), label='returns', color='orange')
    ax1.set_ylabel('returns')
    ax1.legend()

    ax2.plot(((df_data * asset_weights).mean(axis=1) + 1).cumprod(), label='cumulative_returns')
    ax2.set_ylabel('cumulative_returns')
    ax2.legend()
    # plt.savefig(f"./picture/{label}_portfolio_returns.png")
    plt.show()
