# Data dictionary

All values describe the close of `date`, or the completed session ending then. Returns are **decimal fractions**, not percentages; volatility is a **daily** standard deviation, not annualized. Prices and dollar notionals are in synthetic USD. Volumes are shares. Basis points are 0.0001 in decimal price terms.

| Field | Definition / units |
|---|---|
| date | Synthetic business session, YYYY-MM-DD |
| asset_id | Neutral identifier A01–A24 |
| sector | Technology, Financials, Industrials, Energy, Consumer or Healthcare |
| open, high, low, close | Positive synthetic session prices; high/low enclose open/close |
| volume | Positive session share volume |
| bid, ask | End-of-session quotes around close; bid < ask |
| spread_bps | `(ask-bid)/close × 10,000` |
| realized_vol_5d, realized_vol_20d | Sample standard deviation of the latest 5/20 close-to-close daily returns, including today; lower bound 0.001 |
| return_1d, return_5d, return_20d | `close / close_n_sessions_ago − 1`, including today's completed return |
| price_strength_20, price_strength_60 | `close / trailing_mean(close, n) − 1`, including today |
| volume_zscore | `(volume − trailing_20_mean(volume)) / trailing_20_population_std(volume)`, including today |
| volume_trend | Trailing 5-session mean volume / trailing 20-session mean volume − 1 |
| market_return | Equal-weight average of all 24 completed daily asset returns |
| sector_return | Equal-weight average of the four completed daily returns in this asset's sector |
| market_volatility | Sample standard deviation of the last 20 market returns, including today; lower bound 0.001 |
| sector_dispersion | Population standard deviation of today's four asset returns in the sector |
| macro_factor_1, macro_factor_2, macro_factor_3 | Contemporaneously published synthetic macro indicators, arbitrary units, common across assets on a date |
| sentiment_score | Observed synthetic sentiment measure, signed arbitrary units |
| liquidity_score | Observed liquidity measure, 0.1–1.0; larger means more liquid |
| flow_index | Noisy observed signed trading-flow measure, arbitrary units |
| carry_score | Slowly varying observed asset characteristic, signed arbitrary units |
| event_intensity | Nonnegative observed event activity, bounded at 3 |
| event_flag | 1 when event_intensity > 1, else 0 |
| intraday_range | `(high-low)/close`, decimal fraction |

Rolling features at the first supplied date were initialized using earlier observations. Data contains no missing asset sessions, corporate actions or executable labels. A field's name does not imply that it predicts anything. Indicators may overlap, change meaning over time, or contain mostly noise. Data is synthetic and should not be interpreted as evidence about real securities.

Development and validation must be kept conceptually separate. The starter reads validation only when `--split validation` is explicitly requested; it then supplies preceding development rows as history without scoring them.
