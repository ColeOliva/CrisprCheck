from typing import Dict, List, Tuple

from Bio import SeqIO
from Bio.Seq import Seq


def _matches_pam(pam_seq: str, pam_pattern: str = "NGG") -> bool:
    pam_seq = pam_seq.upper()
    pam_pattern = pam_pattern.upper()
    if len(pam_seq) != len(pam_pattern):
        return False
    for a, b in zip(pam_seq, pam_pattern):
        if b == "N":
            continue
        if a != b:
            return False
    return True


def _hamming_positions(a: str, b: str) -> List[int]:
    assert len(a) == len(b)
    return [i for i, (x, y) in enumerate(zip(a.upper(), b.upper())) if x != y]


def scan_fasta_for_guide(guide: str, fasta_path: str, pam: str = "NGG", max_mismatches: int = 4) -> List[Dict]:
    """Naive PAM-aware scan of a FASTA; returns a list of candidate off-targets

    Each hit dict contains: seq_id, start, end (0-based, inclusive), strand ('+'/'-'), target_seq,
    mismatches (int) and mismatch_positions (list of 0-based positions).
    """
    guide = guide.upper()
    L = len(guide)
    hits = []

    for rec in SeqIO.parse(fasta_path, "fasta"):
        seq = str(rec.seq).upper()
        n = len(seq)
        # scan plus strand: guide (L) followed by PAM (len(pam))
        for i in range(0, n - L - len(pam) + 1):
            pam_seq = seq[i + L : i + L + len(pam)]
            if _matches_pam(pam_seq, pam):
                target = seq[i : i + L]
                mism_pos = _hamming_positions(guide, target)
                if len(mism_pos) <= max_mismatches:
                    hits.append(
                        {
                            "seq_id": rec.id,
                            "start": i,
                            "end": i + L - 1,
                            "strand": "+",
                            "target_seq": target,
                            "mismatches": len(mism_pos),
                            "mismatch_positions": mism_pos,
                        }
                    )
        # scan reverse complement (map coords back to original)
        rc = str(Seq(seq).reverse_complement())
        for i in range(0, n - L - len(pam) + 1):
            pam_seq = rc[i + L : i + L + len(pam)]
            if _matches_pam(pam_seq, pam):
                target_rc = rc[i : i + L]
                target = str(Seq(target_rc).reverse_complement())
                mism_pos = _hamming_positions(guide, target)
                if len(mism_pos) <= max_mismatches:
                    # map rc coords to original
                    orig_end = n - i - 1 - len(pam)
                    orig_start = orig_end - (L - 1)
                    hits.append(
                        {
                            "seq_id": rec.id,
                            "start": orig_start,
                            "end": orig_end,
                            "strand": "-",
                            "target_seq": target,
                            "mismatches": len(mism_pos),
                            "mismatch_positions": mism_pos,
                        }
                    )
    return hits
