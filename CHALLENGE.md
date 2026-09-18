# Can you discover and systematically exploit structure in an unfamiliar financial market?

You receive several years of synthetic daily data for 24 assets in six sectors. You do not need professional trading experience. Your task is to identify a plausible relationship, convert it into portfolio positions, and investigate whether it survives costs, risk constraints, and chronological validation.

There is no single intended solution. Momentum, reversal, relative value, statistical models, ranking, portfolio construction, volatility scaling, and combinations are all legitimate avenues. Cash, long-only and long/short strategies are allowed. Complexity receives no automatic credit.

## Data and validation

| Period | Dates | Use |
|---|---|---|
| Development | January 1, 2021–June 28, 2024 | Research and internal chronological experiments |
| Public validation | July 1–December 31, 2024 | Evaluate a substantially frozen approach |
| Unseen evaluation | Calendar year 2025 | Evaluated privately after the deadline |

Sessions use a synthetic weekday calendar, including some real-world holidays. Development has 911 sessions and validation has 132. All 24 assets have an observation on every session; missing values and corporate actions are intentionally excluded. Earlier observations were used to initialize rolling fields at the beginning of development. Those earlier raw observations are not supplied.

Do not randomly shuffle time-series observations into train/test sets. If you change a strategy after seeing validation, acknowledge that validation has become part of your development process. Avoid repeated parameter searches against it. A disappointing result with careful reasoning can still be a strong submission.

## Suggested work plan: 4–6 focused hours

| Activity | Approximate time |
|---|---|
| Understand data and conventions | 30–45 minutes |
| Explore and formulate a hypothesis | 60–90 minutes |
| Implement and backtest | 60–90 minutes |
| Validate, stress costs and inspect risk | 45–60 minutes |
| Write the research note and check reproduction | 45–60 minutes |

The schedule is guidance, not a time-tracking requirement. One thoughtful idea is sufficient. You do not need to try every model or feature.

## What to submit

A private GitHub repository named `disrupt-quant-2026-firstname-lastname` containing:

```text
strategy.py          # required entry point
README.md            # reproduction instructions and disclosure
research_note.pdf    # maximum 2 pages
requirements.txt    # pinned assessment packages or a subset
src/                 # optional Python helpers
artifacts/           # optional CSV/JSON model parameters
analysis.ipynb       # optional research notebook; not executed by evaluation
```

You may retain the public challenge files. The evaluator loads only `strategy.py`, optional Python/CSV/JSON files in `src/` and `artifacts/`, and the approved scientific environment. Do not rely on root files other than `strategy.py` at runtime. Do not load serialized executable objects such as pickle or joblib files. Train using the provided history or store plain CSV/JSON parameters learned only from permissible development observations.

## Research note: maximum two pages

Address these points concisely:

1. **Hypothesis:** What relationship are you attempting to exploit, and why might it exist?
2. **Evidence:** What convinced you it might be real? Report failed or conflicting evidence too.
3. **Construction:** How do signals become positions, and how did you choose parameters?
4. **Risk:** Explain sizing, diversification, leverage, and expected failure conditions.
5. **Costs:** Show their effect and how they influenced turnover or trading decisions.
6. **Validation:** Separate development and validation; report changes made after validation and at least one sensitivity check.
7. **Limitations:** Describe overfitting risks, uncertainty, and when the approach might stop working.
8. **Next step:** What one further investigation would be most useful?

## Assessment: 100 points

| Component | Points |
|---|---:|
| Unseen performance after costs: risk-adjusted return, drawdown and consistency | 30 |
| Robustness across periods, cost scenarios and portfolio concentration | 20 |
| Quantitative research and reasoning | 20 |
| Code correctness, clarity and reproducibility | 15 |
| Risk management | 10 |
| Communication | 5 |

The evaluator also examines monthly and shorter-period results, exposure attribution, and uncertainty. One lucky directional position should not decide the outcome. Scoring caps unusually extreme numerical outcomes, and human review carries half the available points.
