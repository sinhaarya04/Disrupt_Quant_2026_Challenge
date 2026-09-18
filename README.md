# Disrupt Quant — 2026 Quantitative  Challenge

Markets rarely tell you which variables matter, which relationships will persist, or whether a pattern represents genuine structure rather than noise. Approach this unfamiliar multi-asset market as a quantitative researcher: develop a systematic strategy supported by evidence, disciplined validation, and sound risk management.

**Released:** Thursday, September 17, 2026  
**Deadline:** Sunday, September 20, 2026 at 11:59 PM Eastern Time

The challenge is designed for approximately **4–6 hours of focused work**. You are not expected to spend the entire three-day window working on it. The window lets you work around academic and personal commitments.

## Start here

Use Python 3.12 or 3.13; the evaluation environment uses Python 3.13. No GPU or container software is required on your laptop.

```bash
# Clone the challenge repository using the URL in your invitation,
# or unzip the supplied candidate archive and enter its directory.
cd Disrupt_Quant_2026_Challenge
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python starter/backtester.py
```

The command evaluates the equal-weight example on development data and writes metrics, daily returns and six diagnostic plots to `results/development/`.

1. Read [CHALLENGE.md](CHALLENGE.md), [RULES.md](RULES.md), and the [data dictionary](data/data_dictionary.md).
2. Research development data and edit **the root `strategy.py`**.
3. Freeze your approach before inspecting validation performance. Run validation explicitly:

```bash
python starter/backtester.py --split validation
python starter/backtester.py --split validation --cost-multiplier 1.5
python validate_submission.py --starter-check
```

4. Write a research note of at most two pages as `research_note.pdf` and update this README with reproduction instructions and AI disclosure.
5. Run `python validate_submission.py`. Submit your private repository URL and full 40-character commit SHA through the form linked in your invitation. Grant access to the reviewer account specified in that invitation.

Sophisticated machine-learning models are not inherently preferred. A simple strategy supported by strong reasoning, robust validation, and thoughtful risk management may score better than a complex model.

Your final ranking will not be determined solely by P&L or Sharpe ratio. We care about how you think, test hypotheses, manage risk, and support conclusions with evidence.

## Your submission README

Replace or extend this section:

- Candidate name:
- Strategy name and 2–3 sentence summary:
- Reproduction command and environment:
- Development and validation metrics, with dates:
- Important assumptions and known limitations:
- AI tools used:
- How they were used:

Only documentation, the example, and market observations are provided. Any explanatory research examples in `starter/` demonstrate the API; they are not trading recommendations.
