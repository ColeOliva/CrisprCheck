from crispr_check import scoring


def test_scores_drop_with_mismatch():
    guide = "GAGTCCGAGCAGAAGAAGA"
    exact = guide
    one_mismatch = "AAGTCCGAGCAGAAGAAGA"  # single mismatch at pos 0
    s_exact = scoring.position_weighted_score(guide, exact)
    s_one = scoring.position_weighted_score(guide, one_mismatch)
    assert s_exact > s_one
    m_exact = scoring.mit_like_score(guide, exact)
    m_one = scoring.mit_like_score(guide, one_mismatch)
    assert m_exact > m_one
