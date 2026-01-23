"""Create a layman-friendly summary from a crispr_check `results.csv`.

Usage:
  python tools/summarize_results.py results.csv results_human.csv

The script adds a `summary` column with plain-English interpretation of the match
and a `risk_level` bucket based on the numeric `score`.
"""
import csv
import sys
from pathlib import Path


def interpret_score(score: float) -> str:
    if score >= 90:
        return "High — predicted active (likely on-target)"
    if score >= 70:
        return "Moderate — possible activity"
    if score >= 40:
        return "Low — unlikely to be highly active"
    return "Very low — unlikely active"


def parse_positions(tok: str):
    tok = tok.strip()
    if not tok or tok in ("[]", "None"):
        return []
    tok = tok.strip("[]")
    if not tok:
        return []
    return [int(x) for x in tok.split(",")]


def human_positions(pos_list):
    # convert to 1-based positions for readability
    if not pos_list:
        return "None"
    return ",".join(str(p + 1) for p in pos_list)


def summarize_row(row):
    mismatches = int(row.get("mismatches", 0))
    pos_tok = row.get("mismatch_positions", "[]")
    positions = parse_positions(pos_tok)
    score = float(row.get("score", 0.0))
    score_desc = interpret_score(score)

    if mismatches == 0:
        summary = f"Exact match. {score_desc} (score={score:.2f})."
    else:
        pos_text = human_positions(positions)
        plural = "s" if mismatches != 1 else ""
        summary = (
            f"{mismatches} mismatch{plural} at position(s) {pos_text}. {score_desc} (score={score:.2f})."
        )

    # risk level bucket for quick scanning
    if score >= 90:
        risk = "high"
    elif score >= 70:
        risk = "moderate"
    elif score >= 40:
        risk = "low"
    else:
        risk = "very_low"

    return summary, risk


def main(argv):
    if len(argv) < 3:
        print("Usage: python tools/summarize_results.py results.csv results_human.csv")
        return 1
    src = Path(argv[1])
    dst = Path(argv[2])
    if not src.exists():
        print("Source not found:", src)
        return 2

    with src.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    extra = ["summary", "risk_level"]
    out_fields = fieldnames + [f for f in extra if f not in fieldnames]

    with dst.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=out_fields)
        writer.writeheader()
        for r in rows:
            summary, risk = summarize_row(r)
            r["summary"] = summary
            r["risk_level"] = risk
            writer.writerow(r)

    print("Wrote", dst)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
