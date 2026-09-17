# Rules and execution conventions

## Strategy interface

```python
def generate_positions(history, current_date):
    # history: pandas DataFrame through current_date's market close, inclusive
    # current_date: pandas.Timestamp of that close
    return {"A01": 0.08, "A02": -0.06}
```

Positive weights are long, negative weights are short. Missing assets have a zero target; `{}` means cash. Values must be finite numbers, not strings. History is sorted by date and asset identifier. It contains all available earlier rows, with no future observations. The initial call for development uses the first development close; the first earned return is the next session.

Each evaluated period starts from **$1,000,000 in cash** and a fresh strategy instance. Public validation receives development observations as historical context. Private evaluation receives the preceding public observations as context, then new observations one day at a time. Those initial history rows do not earn scored returns. Module state persists within one period, but is reset between periods. No warm-up calls are replayed: initialize rolling/model state from the supplied history on your first call. Avoid reliance on wall-clock time, network services, nondeterministic randomness, or process-global files.

## Information and execution timing

On close **t**, the strategy observes data through that close and requests target weights. It executes at the **open of t+1**, using that open's prices. It does not earn the close-t-to-open-t+1 move on newly requested holdings. Any positions already held from the previous session do earn that overnight move.

At the open, the engine marks previous holdings to the opening prices, computes opening NAV, and sizes the new target dollar holdings as target weights times that opening NAV. Costs are deducted from cash. The new holdings then earn the open-to-close return on t+1. The resulting holdings and cash are carried overnight. This accounts for weight drift; unchanged requested weights may still require small rebalancing trades.

The last session includes compulsory liquidation at its close, with closing observed costs. There is no uncharged open position at the end. Each period charges its own initial establishment and terminal liquidation. Split returns therefore should not be concatenated as if they were one continuous portfolio.

## Portfolio constraints

| At each execution, relative to pre-cost opening NAV | Limit |
|---|---:|
| Per asset | −20% to +20% |
| Gross exposure: sum of absolute weights | 200% |
| Absolute net exposure: absolute sum of weights | 100% |
| Absolute **net** exposure within each sector | 50% |

The engine first clips individual weights, then scales the whole vector by the smallest factor needed to satisfy every aggregate limit. It does not find an optimal replacement portfolio. Invalid identifiers, nonfinite values, wrong return types and extremely large numbers fail validation. Constraint adjustments are reported. Fees and subsequent price changes can cause weights relative to later NAV to drift beyond their execution limits. Cash earns zero and financing/stock-borrow charges are omitted for this assessment; discuss this simplification when relevant.

## Transaction costs

For each asset, let `delta` be traded dollars divided by opening NAV and let `N` be opening NAV. The estimated one-way price cost is:

```text
participation = abs(delta) × N / (previous_volume × previous_close)
impact = 0.10 × previous_realized_vol_20d × sqrt(participation)
         / sqrt(clip(previous_liquidity_score, 0.1, 1.0))
one_way_rate = previous_spread_bps / 20,000 + impact
cost_as_fraction_of_opening_NAV = abs(delta) × one_way_rate
```

Costs use only the previous observed close's liquidity, spread, volatility and volume estimates. They do not use t+1's eventual daily volume. Trade size therefore matters, and a short sale incurs the same trading costs as a purchase of the same size. Bid and ask are quotes at the observed close, not guaranteed next-open quotes. There is no additional quote fill plus spread charge: the half-spread is already in this formula.

Daily turnover is traded notional divided by opening NAV; it is **not divided by two**. Terminal liquidation is included. Reported transaction costs are the sum of daily cost fractions relative to preceding closing NAV, not the difference between separately compounded gross and net returns. Costs are stress-tested at 1×, 1.5× and 2×, holding strategy decisions fixed while recomputing NAV and trade sizes.

## Runtime and reproducibility

The private evaluator allows 2 CPU cores, 4 GB RAM, 256 MB temporary disk, at most 64 processes/threads, 60 seconds per decision and 30 minutes per evaluated period. It uses Python 3.13 and the exact versions in `requirements.txt`. Most standard strategies should be much faster. Prefer fitting once or periodically, rather than refitting an expensive model daily. Use `n_jobs=1` or threading; creation of child processes and shell execution is disabled.

No network, credentials, extra package installation, GPU, external data services or persistent filesystem are available. Only approved Python helpers and CSV/JSON artifacts are supplied. The submitted repository must have at most 1,000 tracked files and 80 MB total tracked content; executable source and selected artifacts total at most 20 MB, with no individual selected file over 10 MB. No symlinks or submodules.

## AI policy — assessment configuration

Candidates may use documentation, search engines, and AI-assisted development tools. Candidates are responsible for understanding every part of their submission and must disclose material use of generative AI. You may be asked to explain, modify, or defend your strategy during subsequent interviews.

Disclose in your README and submission form:

```text
AI tools used:
How they were used:
```

AI use is not automatically penalized. Complete your own research and do not share strategies, code, private data, or results with other applicants. Attribute external code or material assistance. Similarity flags prompt human review and are not automatic proof of misconduct.

Do not attempt to access other submissions, private evaluation material, host files, evaluator processes, or information beyond the history provided. Do not exploit the execution environment or intentionally exhaust resources.

## Deadline and final commit

Submit by **Sunday, September 20, 2026 at 11:59 PM Eastern Time**. The form timestamp and full submitted SHA are authoritative. Commit timestamps are supporting evidence only. A submission timestamp strictly before September 21 at 12:00 AM America/New_York is on time. The submitted commit must already exist when submitted. Later commits are ignored. Keep the repository private and give the organizer's specified reviewer account access before the deadline.

Report technical issues to the organizer through the contact supplied with your invitation. Any accommodation or material rule correction must be communicated consistently to all affected applicants.
