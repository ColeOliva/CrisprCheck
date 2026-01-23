import os

from crispr_check import scoring


def test_load_published_and_score():
    here = os.path.dirname(__file__)
    table = scoring.load_published_cfd()
    assert "pos_weights" in table and "sub_weights" in table

    # use a 20-nt guide to match the published table length
    guide = "GAGTCCGAGCAGAAGAAGAA"
    # create a target that differs at position 5 (0-based) by substituting base
    # that is present in the table mapping; pick guide[5] and change it
    g = guide
    t_list = list(g)
    # flip pos 5 to a different base deterministically
    orig = t_list[5]
    alt = {"A":"C","C":"G","G":"A","T":"C"}[orig]
    t_list[5] = alt
    target = "".join(t_list)

    # compute score via the table-backed scorer
    score_tbl = scoring.cfd_score_with_table(guide, target, table)

    # compute expected multiplicative penalty manually using table values
    pos_w = table["pos_weights"][5]
    sub_w = table["sub_weights"].get((orig, alt), 0.85)
    expected = (1.0 - (pos_w * sub_w)) * 100.0

    assert abs(score_tbl - expected) < 1e-6
