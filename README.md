# CrisprCheck — CRISPR Off‑target Quick‑check ✨

**Lightweight, local tool for quick off-target scanning and explainable scoring**

Goal: Fast, offline-friendly checks of candidate gRNAs against a reference FASTA. Intended for education, teaching, and small labs (not clinical use).

## Quickstart

Install (developer):

- Create a venv: `python -m venv .venv && .venv\Scripts\activate`
- Install: `pip install -e .[dev]`

Run a simple local search (demo FASTA provided in tests):

```
python -m crispr_check.cli search --guide GAGTCCGAGCAGAAGAAGA --pam NGG --fasta tests/data/small.fa --out results.csv
```

## Week 1 (MVP) — checklist ✅
- [x] Basic PAM-aware scanning and mismatch enumeration
- [x] Position-weighted scoring + simple MIT-like score
- [x] CLI `search` subcommand + CSV/TSV output
- [x] Unit tests for scanning and scoring

## Notes & Caveats ⚠️
- This is an educational tool — **not** for clinical decision making. Wet-lab validation required.

---

See `ISSUES.md` for the recommended first issues to open.