from crispr_check import scoring


def test_cfd_exact_match():
    guide = "GAGTCCGAGCAGAAGAAGA"
    target = guide
    s = scoring.cfd_score(guide, target)
    assert 99.9 <= s <= 100.0


def test_cfd_single_mismatch_reduces_score():
    guide = "GAGTCCGAGCAGAAGAAGA"
    t1 = "AAGTCCGAGCAGAAGAAGA"  # mismatch at pos 0
    s_exact = scoring.cfd_score(guide, guide)
    s_one = scoring.cfd_score(guide, t1)
    assert s_one < s_exact


def test_cfd_pam_penalty_and_position_sensitivity():
    guide = "GAGTCCGAGCAGAAGAAGA"
    # mismatch at PAM-proximal (last base)
    t_end = list(guide)
    t_end[-1] = "A" if t_end[-1] != "A" else "C"
    t_end = "".join(t_end)
    # mismatch at PAM-distal (first base)
    t_start = list(guide)
    t_start[0] = "A" if t_start[0] != "A" else "C"
    t_start = "".join(t_start)

    s_start = scoring.cfd_score(guide, t_start)
    s_end = scoring.cfd_score(guide, t_end)
    # PAM-proximal mismatch should be penalized more (lower score) than PAM-distal
    assert s_end < s_start

    # non-canonical PAM penalty
    s_pam = scoring.cfd_score(guide, guide, pam="NNN")
    assert s_pam < scoring.cfd_score(guide, guide, pam="NGG")


def test_cfd_invalid_length_asserts():
    with __import__("pytest").raises(AssertionError):
        scoring.cfd_score("AAA", "AA")
