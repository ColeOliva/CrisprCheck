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
    # allow shorter guides (trimmed from canonical 20 nt) to match when the PAM
    # appears a few bases downstream of the truncated guide. Use a small
    # canonical length to derive a reasonable search offset.
    CANONICAL_GUIDE_LEN = 20
    max_offset = max(0, CANONICAL_GUIDE_LEN - L)

    for rec in SeqIO.parse(fasta_path, "fasta"):
        seq = str(rec.seq).upper()
        n = len(seq)
        # scan plus strand: guide (L) possibly followed by PAM within a small
        # downstream offset when guides are shorter than canonical length.
        for i in range(0, n - L - len(pam) + 1):
            # check possible offsets for the PAM (0 means immediately adjacent)
            for off in range(0, max_offset + 1):
                start_pam = i + L + off
                pam_seq = seq[start_pam : start_pam + len(pam)]
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
                    # once a PAM is matched for this window, don't record the
                    # same target multiple times for other offsets
                    break
        # scan reverse complement (map coords back to original)
        rc = str(Seq(seq).reverse_complement())
        for i in range(0, n - L - len(pam) + 1):
            for off in range(0, max_offset + 1):
                start_pam = i + L + off
                pam_seq = rc[start_pam : start_pam + len(pam)]
                if _matches_pam(pam_seq, pam):
                    target_rc = rc[i : i + L]
                    # rc already contains the forward-oriented guide when the
                    # original sequence carries the reverse-complemented target.
                    # So use the substring directly for comparison.
                    target = target_rc
                    mism_pos = _hamming_positions(guide, target)
                    if len(mism_pos) <= max_mismatches:
                        # map rc coords back to original sequence indices
                        orig_start = n - i - L
                        orig_end = n - i - 1
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
                    break
    return hits
