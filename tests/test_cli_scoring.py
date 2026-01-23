import os
import csv
import tempfile

from types import SimpleNamespace
from crispr_check import cli, scoring


def run_search_and_read_scores(score_method):
    here = os.path.dirname(__file__)
    fasta = os.path.join(here, "data", "small.fa")
    guide = "GAGTCCGAGCAGAAGAAGA"
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".csv") as tmp:
        out = tmp.name
    args = SimpleNamespace(guide=guide, pam="NGG", fasta=fasta, out=out, max_mismatches=4, score_method=score_method, pretty=False)
    cli.search_command(args)
    rows = []
    with open(out, newline="") as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            rows.append(r)
    return guide, rows


def test_cli_scores_pw():
    guide, rows = run_search_and_read_scores("pw")
    assert len(rows) >= 1
    for r in rows:
        target = r["target_seq"]
        expected = scoring.position_weighted_score(guide, target)
        assert abs(float(r["score"]) - expected) < 1e-6


def test_cli_scores_mit():
    guide, rows = run_search_and_read_scores("mit")
    assert len(rows) >= 1
    for r in rows:
        target = r["target_seq"]
        expected = scoring.mit_like_score(guide, target)
        assert abs(float(r["score"]) - expected) < 1e-6


def test_cli_scores_cfd():
    guide, rows = run_search_and_read_scores("cfd")
    assert len(rows) >= 1
    for r in rows:
        target = r["target_seq"]
        expected = scoring.cfd_score(guide, target, pam="NGG")
        assert abs(float(r["score"]) - expected) < 1e-6
