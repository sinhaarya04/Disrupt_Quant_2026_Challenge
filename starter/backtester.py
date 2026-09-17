"""Trusted local research engine. Do not use this process for untrusted submissions.

Close t observations -> open t+1 execution. Existing holdings earn the gap;
new targets earn open-to-close. Fees are paid from cash. No same-close fills.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path
import sys
import numpy as np
import pandas as pd

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from starter.metrics import summarize, plot_results

INITIAL_NAV = 1_000_000.0
IMPACT_COEFFICIENT = 0.10


def load_data(path):
    data = pd.read_csv(path, parse_dates=['date'])
    return data.sort_values(['date', 'asset_id']).reset_index(drop=True)


def validate_market(data):
    needed = {'date', 'asset_id', 'sector', 'open', 'close', 'volume', 'spread_bps', 'realized_vol_20d', 'liquidity_score'}
    if not needed.issubset(data):
        raise ValueError(f'Missing market columns: {needed - set(data)}')
    if data.duplicated(['date', 'asset_id']).any():
        raise ValueError('Duplicate asset/date')
    sizes = data.groupby('date').size()
    universe = sorted(data.asset_id.unique())
    if (sizes != len(universe)).any():
        raise ValueError('This engine requires one observation per asset per session')
    for col in ['open', 'close', 'volume', 'spread_bps', 'realized_vol_20d', 'liquidity_score']:
        if not np.isfinite(data[col]).all() or (data[col] <= 0).any():
            raise ValueError(f'Invalid market values in {col}')
    if (data.groupby('asset_id').sector.nunique() != 1).any():
        raise ValueError('Sector changes unsupported')


def constrain_positions(output, assets, sectors):
    if not isinstance(output, dict):
        raise ValueError('generate_positions must return dict[str, float]')
    if len(output) > len(assets) or any(k not in assets for k in output):
        raise ValueError('Unknown asset identifier')
    if any(isinstance(v, (bool, str)) or not isinstance(v, (int, float, np.number)) for v in output.values()):
        raise ValueError('Weights must be finite numbers')
    raw = np.array([output.get(a, 0.0) for a in assets], dtype=float)
    if not np.isfinite(raw).all() or np.any(np.abs(raw) > 1e6):
        raise ValueError('Nonfinite or excessively large target')
    target = np.clip(raw, -.2, .2)
    # A common scale preserves signs and proportions after per-asset clipping.
    scale = min(1., 2. / max(np.abs(target).sum(), 1e-12),
                1. / max(abs(target.sum()), 1e-12))
    for sector in np.unique(sectors):
        scale = min(scale, .5 / max(abs(target[sectors == sector].sum()), 1e-12))
    target *= scale
    return target, float(np.abs(raw - target).sum())


def trading_cost(delta, observed, nav, multiplier=1.):
    """Cost per pre-trade NAV, based only on the previous observable close.

    delta: signed traded notionals / pre-trade NAV. volume is shares/session.
    """
    participation = np.abs(delta) * nav / (observed.volume.to_numpy() * observed.close.to_numpy())
    impact = IMPACT_COEFFICIENT * observed.realized_vol_20d.to_numpy() * np.sqrt(participation)
    impact /= np.sqrt(np.clip(observed.liquidity_score.to_numpy(), .1, 1.))
    rate = observed.spread_bps.to_numpy() / 20_000 + impact
    return multiplier * np.abs(delta) * rate


def simulate(data, decide, start=None, end=None, cost_multiplier=1., initial_nav=INITIAL_NAV, liquidate=True):
    """decide receives a copy of history and pd.Timestamp for latest observed close.

    Split dates refer to earned-return dates. Each run starts from cash. Prior
    rows are history only. Terminal liquidation is charged at the last close.
    """
    data = data.sort_values(['date', 'asset_id']).reset_index(drop=True)
    validate_market(data)
    dates = pd.DatetimeIndex(data.date.unique())
    assets = sorted(data.asset_id.unique())
    n = len(assets)
    sectors = data.iloc[:n].sector.to_numpy()
    first = pd.Timestamp(start) if start else dates[1]
    last = pd.Timestamp(end) if end else dates[-1]
    eligible = [i for i in range(1, len(dates)) if first <= dates[i] <= last]
    if not eligible:
        raise ValueError('No sessions with previous-close history in requested period')
    nav = float(initial_nav)
    old = np.zeros(n)  # previous-close risky dollar holdings / previous-close NAV
    rows, details, targets = [], [], []
    for i in eligible:
        observed = data.iloc[(i-1)*n:i*n].reset_index(drop=True)
        current = data.iloc[i*n:(i+1)*n].reset_index(drop=True)
        history = data.iloc[:i*n].copy(deep=True)
        output = decide(history, dates[i-1])
        target, adjustment = constrain_positions(output, assets, sectors)
        gap = current.open.to_numpy() / observed.close.to_numpy() - 1
        gap_pnl = old * gap
        opening_factor = 1 + gap_pnl.sum()
        if opening_factor <= 0:
            raise ValueError('Portfolio insolvent at open')
        opening_nav = nav * opening_factor
        drifted = old * (1 + gap) / opening_factor
        delta = target - drifted
        fees = trading_cost(delta, observed, opening_nav, cost_multiplier)
        intraday = current.close.to_numpy() / current.open.to_numpy() - 1
        intraday_pnl = opening_factor * target * intraday
        fee_pnl = opening_factor * fees
        end_factor = opening_factor * (1 + (target * intraday).sum() - fees.sum())
        if end_factor <= 0:
            raise ValueError('Portfolio insolvent at close')
        close_weights = opening_factor * target * (1 + intraday) / end_factor
        turnover = np.abs(delta).sum()
        if liquidate and i == eligible[-1]:
            exit_fees = trading_cost(-close_weights, current, nav * end_factor, cost_multiplier)
            fee_pnl += end_factor * exit_fees
            turnover += end_factor / opening_factor * np.abs(close_weights).sum()
            end_factor *= 1 - exit_fees.sum()
            close_weights[:] = 0
        gross_contrib = gap_pnl + intraday_pnl
        net_return = float(end_factor - 1)
        rows.append({'date': dates[i], 'net_return': net_return,
                     'gross_return': float(gross_contrib.sum()), 'cost_fraction': float(fee_pnl.sum()),
                     'turnover': float(turnover), 'gross_exposure': float(np.abs(target).sum()),
                     'net_exposure': float(target.sum()), 'constraint_adjustment': adjustment,
                     'nav': nav * end_factor,
                     'market_return': float(current.close.sum() * 0 + current.market_return.iloc[0]) if 'market_return' in current else float(gap.mean()),
                     'maximum_asset_weight': float(np.abs(target).max()),
                     'maximum_sector_net': max(abs(target[sectors == s].sum()) for s in np.unique(sectors))})
        for j, asset in enumerate(assets):
            details.append({'date': dates[i], 'asset_id': asset, 'sector': sectors[j],
                            'target': target[j], 'previous_weight': old[j], 'trade': delta[j],
                            'gross_contribution': gross_contrib[j], 'cost_contribution': fee_pnl[j],
                            'net_contribution': gross_contrib[j] - fee_pnl[j],
                            'dollar_pnl': nav * (gross_contrib[j] - fee_pnl[j]),
                            'long_gross': max(old[j], 0) * gap[j] + opening_factor * max(target[j], 0) * intraday[j],
                            'short_gross': min(old[j], 0) * gap[j] + opening_factor * min(target[j], 0) * intraday[j]})
        targets.append(target.copy())
        nav *= end_factor
        old = close_weights
    return pd.DataFrame(rows), pd.DataFrame(details)


def import_strategy(path):
    """Only use with your own, trusted research code."""
    path = Path(path).resolve()
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location('candidate_strategy', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.generate_positions


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--strategy', type=Path, default=root / 'strategy.py')
    parser.add_argument('--split', choices=['development', 'validation'], default='development')
    parser.add_argument('--out', type=Path, default=root / 'results')
    parser.add_argument('--cost-multiplier', type=float, default=1.)
    args = parser.parse_args()
    data = load_data(root / 'data/development.csv')
    start = None
    if args.split == 'validation':
        validation = load_data(root / 'data/validation.csv')
        start = str(validation.date.min().date())
        data = pd.concat([data, validation], ignore_index=True)
    daily, attribution = simulate(data, import_strategy(args.strategy), start=start, cost_multiplier=args.cost_multiplier)
    out = args.out / args.split
    out.mkdir(parents=True, exist_ok=True)
    daily.to_csv(out / 'daily.csv', index=False)
    attribution.to_csv(out / 'attribution.csv', index=False)
    metrics = summarize(daily)
    (out / 'metrics.json').write_text(json.dumps(metrics, indent=2, allow_nan=False))
    plot_results(daily, out / 'diagnostics.png')
    print(json.dumps(metrics, indent=2))
    print(f'Results: {out}')


if __name__ == '__main__':
    main()
