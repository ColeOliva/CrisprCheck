from crispr_check import scoring


def test_cfd_full_exact_and_single_mismatch():
    guide = "GAGTCCGAGCAGAAGAAGA"
    exact = guide
    one_mismatch = "AAGTCCGAGCAGAAGAAGA"
    s_exact = scoring.cfd_score_full(guide, exact)
    s_one = scoring.cfd_score_full(guide, one_mismatch)
    assert s_exact > s_one
    assert 0 <= s_one < s_exact <= 100


def test_cfd_full_position_sensitivity():
    guide = "GAGTCCGAGCAGAAGAAGA"
    # mismatch near PAM (last base)
    t_end = list(guide)
    t_end[-1] = "A" if t_end[-1] != "A" else "C"
    t_end = "".join(t_end)
    # mismatch near distal (first base)
    t_start = list(guide)
    t_start[0] = "A" if t_start[0] != "A" else "C"
    t_start = "".join(t_start)

    s_start = scoring.cfd_score_full(guide, t_start)
    s_end = scoring.cfd_score_full(guide, t_end)
    assert s_end < s_start


def test_cfd_full_pam_penalty():
    guide = "GAGTCCGAGCAGAAGAAGA"
    s_ngg = scoring.cfd_score_full(guide, guide, pam="NGG")
    s_non = scoring.cfd_score_full(guide, guide, pam="NNN")
    assert s_non < s_ngg
