# CrisprCheck — CRISPR Off‑target Quick‑check

Scope
- Lightweight, offline-friendly tool to scan a candidate gRNA against a reference FASTA and rank potential off‑target sites with explainable scores.
- Intended for small-scale or teaching use; not for clinical decision-making.

Setup
1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

2. Install package (developer extras):

```bash
pip install -e .[dev]
```


Quick How‑to
- Single search (example):

```bash
python -m crispr_check.cli search --guide GAGTCCGAGCAGAAGAAGA --pam NGG --fasta tests/data/small.fa --out results.csv
```

# Visualization & Analysis
- Plot efficiency/score distributions:

```bash
python -m crispr_check.cli plot results.csv --output eff_plot.png --show
```

- Print summary statistics for efficiency/score columns:

```bash
python -m crispr_check.cli stats results.csv
```

# Web UI (Streamlit)
- Launch an interactive web app for uploading results, visualizing distributions, and downloading plots/statistics:

```bash
streamlit run tools/streamlit_app.py
```


Files of interest
- `crispr_check/search.py`: PAM-aware scanner (both strands).
- `crispr_check/scoring.py`: scoring implementations and the CFD table loader. The project uses Percent‑Active → `weight = 1 - PercentActive` for CFD weights.
- `crispr_check/cli.py`: command-line entrypoint and subcommands (search, plot, stats).
- `crispr_check/visualization.py`: plotting and summary statistics utilities.
- `tools/streamlit_app.py`: Streamlit web UI for results exploration.
- `crispr_check/data/cfd_published.json`: packaged CFD weights (derived from provided FractionActive table).

Development
- Tests: `pytest` (run from project root).
- Format: `black .`

Notes
- The repository ships a derived CFD table based on Percent‑Active from Doench et al.; altering the source metric (e.g., mean delta LFC or −log(p)) will change absolute scores. Use Percent‑Active for compatibility with the published CFD method.

Contributing
- Open issues and PRs against `main`; use feature branches for changes.
