"""Minimal API illustration: a diversified long-only portfolio."""


def generate_positions(history, current_date):
    latest = history[history.date == current_date]
    return dict.fromkeys(latest.asset_id, 1.0 / len(latest))
