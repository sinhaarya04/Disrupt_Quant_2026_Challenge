"""Your submission entry point. Replace the equal-weight baseline below."""


def generate_positions(history, current_date):
    latest = history.loc[history.date == current_date]
    return {asset: 1.0 / len(latest) for asset in latest.asset_id}
