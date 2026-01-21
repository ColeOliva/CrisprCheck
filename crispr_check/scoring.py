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
