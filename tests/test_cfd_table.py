import os
from crispr_check import scoring


def test_cfd_table_loader_and_usage():
    here = os.path.dirname(__file__)
    table_path = os.path.join(here, "data", "cfd_small.json")
    table = scoring.load_cfd_table(table_path)
    guide = "GAGTCCGAGCAGAAGAAGA"
    target = "AAGTCCGAGCAGAAGAAGA"
    s_table = scoring.cfd_score_with_table(guide, target, table)
    s_fallback = scoring.cfd_score_full(guide, target)
    # Using a table should produce a defined score and differ from fallback
    assert 0 <= s_table <= 100
    assert s_table != s_fallback
