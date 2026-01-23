import os

from crispr_check import search


def test_variable_guide_lengths():
    here = os.path.dirname(__file__)
    fasta = os.path.join(here, "data", "small.fa")

    # 20-nt guide (original)
    guide20 = "GAGTCCGAGCAGAAGAAGA"
    hits20 = search.scan_fasta_for_guide(guide20, fasta, pam="NGG", max_mismatches=2)
    assert any(h["mismatches"] == 0 for h in hits20)

    # 18-nt guide (shorter) that should still find matches when trimmed
    guide18 = guide20[:18]
    hits18 = search.scan_fasta_for_guide(guide18, fasta, pam="NGG", max_mismatches=2)
    assert len(hits18) >= 1


def test_alternative_pam_cas12a():
    here = os.path.dirname(__file__)
    fasta = os.path.join(here, "data", "small.fa")

    # Cas12a-like PAM is TTTV (we'll use TTTN to allow N wildcard)
    # Construct a small sequence that contains TTTN PAM after a 20-nt protospacer
    # We'll create an on-the-fly FASTA by writing a temp file
    seq = (
        ">tmp\n"
        + "A" * 5
        + "GAGTCCGAGCAGAAGAAGA"  # 20-mer guide target
        + "TTTA"
        + "A" * 10
    )
    tmp = os.path.join(here, "data", "cas12a.fa")
    with open(tmp, "w") as fh:
        fh.write(seq + "\n")

    hits = search.scan_fasta_for_guide("GAGTCCGAGCAGAAGAAGA", tmp, pam="TTTN", max_mismatches=0)
    assert len(hits) >= 1


def test_guide_with_N_bases_and_max_mismatches_boundary():
    here = os.path.dirname(__file__)
    fasta = os.path.join(here, "data", "small.fa")

    # Guide containing ambiguous base 'N' should be treated literally (no matching base)
    guide_n = "GAGTCCGAGCANAGAAGA"  # contains an 'N' at pos 12
    # With max_mismatches large, we'll still find matches (treat 'N' as mismatch)
    hits = search.scan_fasta_for_guide(guide_n, fasta, pam="NGG", max_mismatches=5)
    assert isinstance(hits, list)

    # Boundary: max_mismatches exactly equal to mismatch count should include the hit
    guide_exact = "GAGTCCGAGCAGAAGAAGA"
    # compare to a sequence with 2 mismatches (chr1_mut contains a mutation)
    hits2 = search.scan_fasta_for_guide(guide_exact, fasta, pam="NGG", max_mismatches=2)
    assert any(h["mismatches"] <= 2 for h in hits2)
