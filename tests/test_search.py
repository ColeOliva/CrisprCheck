import os
from crispr_check import search


def test_scan_fasta_for_guide_exact_and_one_mismatch():
    here = os.path.dirname(__file__)
    fasta = os.path.join(here, "data", "small.fa")
    guide = "GAGTCCGAGCAGAAGAAGA"
    hits = search.scan_fasta_for_guide(guide, fasta, pam="NGG", max_mismatches=2)
    # Expect at least two hits (one exact, one with single mismatch)
    assert len(hits) >= 2
    counts = sorted([h["mismatches"] for h in hits])
    assert 0 in counts
    assert 1 in counts
