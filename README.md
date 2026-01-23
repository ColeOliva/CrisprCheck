# CrisprCheck — CRISPR Off‑target Quick‑check ✨

Lightweight, local tool for quick off-target scanning and explainable scoring.

Purpose
 - Fast, offline-friendly checks of candidate gRNAs against a reference FASTA.
 - Designed for teaching and small-lab use; not for clinical decision-making.

Quickstart
 - Create a venv: `python -m venv .venv && .venv\Scripts\activate`
 - Install (dev): `pip install -e .[dev]`
 - Run a simple local search (demo FASTA under `tests/data`):

```
python -m crispr_check.cli search --guide GAGTCCGAGCAGAAGAAGA --pam NGG --fasta tests/data/small.fa --out results.csv
```

Project Status (high level)
 - Core scanner: `crispr_check/search.py` — PAM-aware scanning, both strands, coordinate mapping.
 - Scoring: `crispr_check/scoring.py` — position-weighted, MIT-like, simplified and fuller CFD approximations, and a table-driven loader.
 - CLI: `crispr-check` entrypoint in `crispr_check/cli.py` with `search` subcommand.
 - Tests: comprehensive unit tests in `tests/` (edge-cases included); CI runs on GitHub Actions.

Roadmap & Next Priorities
 1. Integrate published CFD substitution & positional weights and add tests (improves scoring accuracy).
 2. Batch CLI I/O: accept multiple guides (CSV/TSV/JSON) and add `--out-format` (csv|json|tsv).
 3. Developer tooling: add `pre-commit`, `mypy`, and CI lint/type jobs; enable coverage reporting.
 4. Streamlit demo: minimal interactive app under `app/` to run single-guide checks and display scores.
 5. Performance: add optional FASTA indexing / k-mer seeding for large references and benchmarks.

Contributing
 - Open an issue for a new task or pick an item from the roadmap above.
 - Use feature branches and open PRs against `main`.

Notes & Caveats
 - This is an educational tool — validate any wet-lab work independently.