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
