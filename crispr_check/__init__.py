"""CrisprCheck package"""

__version__ = "0.1.0"

from . import scoring, search
# Re-export score functions for convenience
from .scoring import cfd_score, mit_like_score, position_weighted_score

__all__ = ["search", "scoring", "position_weighted_score", "mit_like_score", "cfd_score"]
