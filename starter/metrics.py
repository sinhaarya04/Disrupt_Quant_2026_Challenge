"""Metrics use daily simple returns, 252 sessions/year and zero cash yield."""
import numpy as np
import pandas as pd


def summarize(daily):
    r = daily['net_return'].to_numpy(float)
    if len(r) == 0:
        raise ValueError('No evaluated sessions')
    nav = np.cumprod(1 + r)
    peak = np.maximum.accumulate(np.r_[1.0, nav])[1:]
    dd = nav / peak - 1
    std = float(r.std(ddof=1)) if len(r) > 1 else 0.0
    downside = float(np.sqrt(np.mean(np.minimum(r, 0) ** 2)))
    annual = float(nav[-1] ** (252 / len(r)) - 1) if nav[-1] > 0 else -1.0
    ratio = lambda numerator, denominator: float(numerator / denominator) if denominator > 1e-12 else None
    result = {
        'sessions': len(r), 'total_return': float(nav[-1] - 1),
        'annualized_return': annual, 'annualized_volatility': std * np.sqrt(252),
        'sharpe': ratio(r.mean() * np.sqrt(252), std),
        'sortino': ratio(r.mean() * np.sqrt(252), downside),
        'maximum_drawdown': float(dd.min()), 'calmar': ratio(annual, -dd.min()),
        'hit_rate': float(np.mean(r > 0)),
        'average_turnover': float(daily.turnover.mean()),
        'annualized_turnover': float(daily.turnover.mean() * 252),
        'transaction_costs': float(daily.cost_fraction.sum()),
        'average_gross_exposure': float(daily.gross_exposure.mean()),
        'maximum_gross_exposure': float(daily.gross_exposure.max()),
        'average_net_exposure': float(daily.net_exposure.mean()),
        'maximum_absolute_net_exposure': float(daily.net_exposure.abs().max()),
        'constraint_adjustment_days': int((daily.constraint_adjustment > 1e-10).sum()),
    }
    return result


def plot_results(daily, path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    r = daily.set_index(pd.to_datetime(daily.date)).net_return
    nav = (1 + r).cumprod()
    peak = np.maximum.accumulate(np.r_[1., nav])[1:]
    vol = r.rolling(63, min_periods=21).std() * np.sqrt(252)
    sharpe = r.rolling(63, min_periods=21).mean() * 252 / vol.replace(0, np.nan)
    with plt.style.context('seaborn-v0_8-whitegrid'):
        fig, axes = plt.subplots(3, 2, figsize=(13, 10), sharex=True)
        values = [nav, nav / peak - 1, vol, sharpe,
                  pd.Series(daily.gross_exposure.to_numpy(), index=r.index),
                  pd.Series(daily.turnover.to_numpy(), index=r.index)]
        titles = ['NAV (initial = 1)', 'Drawdown', '63-session annualized volatility',
                  '63-session Sharpe', 'Gross exposure at execution', 'Traded notional / opening NAV']
        for ax, value, title in zip(axes.flat, values, titles):
            ax.plot(value.index, value, color='#174c67', lw=1.2)
            ax.set_title(title, loc='left', fontsize=11)
        fig.suptitle('Disrupt Quant | Strategy diagnostics', fontsize=17, x=.07, ha='left')
        fig.tight_layout(rect=(0, 0, 1, .96))
        fig.savefig(path, dpi=150)
        plt.close(fig)
