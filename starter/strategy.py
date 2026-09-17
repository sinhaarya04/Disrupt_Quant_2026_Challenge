"""Replace this equal-weight example with your research strategy.

The function is called once per execution day with history through the previous
close. Returning {} means cash. Missing assets receive zero target weight.
"""


def generate_positions(history, current_date):
    latest = history.loc[history.date == current_date]
    return {asset: 1.0 / len(latest) for asset in latest.asset_id}
