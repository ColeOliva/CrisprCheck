from typing import List


def position_weighted_score(guide: str, target: str) -> float:
    """Simple position-weighted score (0-100). Higher is better.

    We penalize mismatches more heavily when closer to the PAM (3' end of the guide).
    """
    g = guide.upper()
    t = target.upper()
    assert len(g) == len(t)
    L = len(g)
    # positions: 0..L-1 where index L-1 is PAM-proximal
    weights = [i + 1 for i in range(L)]  # increasing weight towards PAM
    total = sum(weights)
    mismatches = [i for i, (a, b) in enumerate(zip(g, t)) if a != b]
    penalty = sum(weights[i] for i in mismatches) / total
    score = max(0.0, 1.0 - penalty) * 100.0
    return score


def mit_like_score(guide: str, target: str) -> float:
    """A simplified MIT-like score: multiplicative penalties per mismatch with positional effect.
    This is a simplified proxy for the MIT scheme.
    """
    g = guide.upper()
    t = target.upper()
    assert len(g) == len(t)
    L = len(g)
    # positional penalties (simple, stronger near PAM)
    base_penalties = [0.0] * L
    for i in range(L):
        # make a stronger penalty toward PAM-proximal (end)
        base_penalties[i] = 0.01 + (i / (L * 5.0))
    score = 1.0
    for i, (a, b) in enumerate(zip(g, t)):
        if a != b:
            score *= (1.0 - base_penalties[i])
    return max(0.0, score * 100.0)


def cfd_score(guide: str, target: str, pam: str = "NGG") -> float:
    """Simplified CFD-like score (0-100).  

    This is an educational, simplified implementation inspired by Doench et al. (2016).
    It approximates position-specific and substitution-specific penalties and applies a
    PAM penalty when the PAM does not match the canonical pattern.
    """
    g = guide.upper()
    t = target.upper()
    assert len(g) == len(t), "guide and target must have equal length"
    L = len(g)

    # Positional penalty increases toward the PAM-proximal end (3').
    # Values chosen to mimic stronger effect near PAM without reproducing the full table.
    pos_penalty = [0.02 + (i / max(1, (L - 1))) * 0.18 for i in range(L)]

    # Substitution weight modifiers (guide_base -> target_base). Values <1 reduce penalty.
    # Only a few common cases are given non-default weights for demonstration; default is 1.0.
    sub_weights = {
        ("G", "A"): 0.9,
        ("C", "T"): 0.9,
        ("A", "G"): 0.9,
        ("T", "C"): 0.9,
    }

    score = 1.0
    for i, (a, b) in enumerate(zip(g, t)):
        if a != b:
            w = sub_weights.get((a, b), 1.0)
            penalty = pos_penalty[i] * w
            score *= max(0.0, 1.0 - penalty)

    # PAM penalty: if PAM is not canonical (pattern contains e.g. 'N' wildcard), reduce score.
    # Here we apply a modest penalty when supplied PAM pattern doesn't match expected.
    normalized_pam = pam.upper()
    if normalized_pam != "NGG":
        score *= 0.9

    return max(0.0, score * 100.0)


def cfd_score_full(guide: str, target: str, pam: str = "NGG") -> float:
    """More complete CFD-like score using positional weights and a substitution matrix.

    This implementation is an educational re-creation of the CFD approach: it uses a
    substitution weight for each mismatch type and a positional weight for each guide
    position (20-nt guide assumed). The score is multiplicative across mismatches.
    Returns value scaled 0-100.
    """
    g = guide.upper()
    t = target.upper()
    assert len(g) == len(t), "guide and target must have equal length"
    L = len(g)

    # Positional weights stronger near PAM-proximal (3') end. Sum scaled to ~1.0
    # Using a triangular-like profile for demonstration; in full CFD this is empirical.
    pos_weights = [((i + 1) / float(L)) ** 1.5 for i in range(L)]

    # Substitution penalty weights for mismatch types (guide_base -> target_base).
    # Values in (0,1], where larger means more damaging (higher penalty).
    # These are illustrative and intended for educational MVP; replace with published table for production.
    sub_weights = {
        ("A", "C"): 0.8,
        ("A", "G"): 0.6,
        ("A", "T"): 0.9,
        ("C", "A"): 0.8,
        ("C", "G"): 0.7,
        ("C", "T"): 0.6,
        ("G", "A"): 0.6,
        ("G", "C"): 0.7,
        ("G", "T"): 0.8,
        ("T", "A"): 0.9,
        ("T", "C"): 0.6,
        ("T", "G"): 0.8,
    }

    score = 1.0
    for i, (a, b) in enumerate(zip(g, t)):
        if a != b:
            w = sub_weights.get((a, b), 0.85)
            penalty = pos_weights[i] * w
            score *= max(0.0, 1.0 - penalty)

    # PAM mismatch penalty (if PAM argument is non-canonical, apply mild penalty)
    if pam.upper() != "NGG":
        score *= 0.92

    return max(0.0, score * 100.0)


def load_cfd_table(path: str) -> dict:
    """Load a CFD table from a JSON file.

    Expected JSON format:
    {
      "pos_weights": [float,...],   # length == guide length (e.g., 20)
      "sub_weights": {"A>G": 0.6, ...}
    }

    Returns a dict with keys `pos_weights` (list) and `sub_weights` (dict mapping tuples).
    """
    import json

    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    pos = data.get("pos_weights")
    sub = data.get("sub_weights")
    # normalize substitution keys to tuple form
    sub_norm = {}
    if sub:
        for k, v in sub.items():
            if isinstance(k, str) and ">" in k:
                a, b = k.split(">")
                sub_norm[(a.upper(), b.upper())] = float(v)
    return {"pos_weights": pos, "sub_weights": sub_norm}


def load_published_cfd() -> dict:
    """Load the packaged "published" CFD table shipped with the package.

    This returns the same dict format as `load_cfd_table`. The JSON file is
    stored under `crispr_check/data/cfd_published.json`. Replace this file
    with the official published CFD table values for production.
    """
    import os

    here = os.path.dirname(__file__)
    p = os.path.join(here, "data", "cfd_published.json")
    return load_cfd_table(p)


def cfd_score_with_table(guide: str, target: str, table: dict, pam: str = "NGG") -> float:
    """Compute CFD score using a provided table dict (from `load_cfd_table`).

    Table dict must contain `pos_weights` (list) and `sub_weights` (dict keyed by (a,b)).
    If table is None, falls back to `cfd_score_full` behavior.
    """
    if table is None:
        return cfd_score_full(guide, target, pam=pam)

    g = guide.upper()
    t = target.upper()
    assert len(g) == len(t)
    L = len(g)

    pos_weights = table.get("pos_weights")
    sub_weights = table.get("sub_weights") or {}

    # validate or fallback
    if not pos_weights or len(pos_weights) != L:
        # fallback to generated positional profile
        pos_weights = [((i + 1) / float(L)) ** 1.5 for i in range(L)]

    score = 1.0
    for i, (a, b) in enumerate(zip(g, t)):
        if a != b:
            w = sub_weights.get((a, b), 0.85)
            penalty = pos_weights[i] * w
            score *= max(0.0, 1.0 - penalty)

    if pam.upper() != "NGG":
        score *= 0.92

    return max(0.0, score * 100.0)
