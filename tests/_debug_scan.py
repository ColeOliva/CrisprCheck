import os

from crispr_check import search

here = os.path.dirname(__file__)
# rev case
guide = 'GAGTCCGAGCAGAAGAAGA'

def rc(s):
    comp = {'A':'T','T':'A','G':'C','C':'G'}
    return ''.join(comp.get(c,'N') for c in reversed(s))

rc_target = rc(guide)
rev_pam = 'CCA'
seq = '>rev\n' + 'AAA' + rev_pam + rc_target + 'TTT\n'
tmp = os.path.join(here, 'rev.fa')
with open(tmp,'w') as fh:
    fh.write(seq)
hits = search.scan_fasta_for_guide(guide, tmp, pam='NGG', max_mismatches=0)
print('REV HITS:', hits)
print('DEBUG: guide len =', len(guide))
print('DEBUG: rev.fa contents =', open(tmp).read())
from Bio import SeqIO
# Inspect sequence and reverse complement to debug why rc hits are missed
from Bio.Seq import Seq

for rec in SeqIO.parse(tmp, 'fasta'):
    seq = str(rec.seq).upper()
    n = len(seq)
    print('DEBUG: seq len', n, 'seq=', seq)
    rc = str(Seq(seq).reverse_complement())
    print('DEBUG: rc len', len(rc), 'rc=', rc)
    L = len(guide)
    CANONICAL_GUIDE_LEN = 20
    max_offset = max(0, CANONICAL_GUIDE_LEN - L)
    print('DEBUG: L, max_offset', L, max_offset)
    print('DEBUG: rc.find(guide)=', rc.find(guide))
    for i in range(0, n - L - max_offset - 3 + 1):
        for off in range(0, max_offset + 1):
            start_pam = i + L + off
            pam_seq = rc[start_pam : start_pam + 3]
            print('DEBUG: rc i', i, 'off', off, 'pam_seq', pam_seq)
            if search._matches_pam(pam_seq, 'NGG'):
                target_rc = rc[i : i + L]
                target = str(Seq(target_rc).reverse_complement())
                mism_pos = search._hamming_positions(guide, target)
                print('DEBUG: MATCH at i,off', i, off, 'pam_seq', pam_seq, 'target', target, 'mism_pos', mism_pos)
# multi case
seq2 = '>multi\n' + guide + 'AGG' + 'A' + guide + 'AGG' + '\n'
tmp2 = os.path.join(here, 'multi.fa')
with open(tmp2,'w') as fh:
    fh.write(seq2)
hits2 = search.scan_fasta_for_guide(guide, tmp2, pam='NGG', max_mismatches=0)
print('MULTI HITS:', hits2)
print('DEBUG: multi.fa contents =', open(tmp2).read())
# show where guide and PAM occur in the original multi sequence
from Bio import SeqIO

for rec in SeqIO.parse(tmp2, 'fasta'):
    seq = str(rec.seq).upper()
    print('DEBUG: seq len', len(seq), 'seq=', seq)
    # find all occurrences of guide
    idx = seq.find(guide)
    occ = []
    while idx != -1:
        occ.append(idx)
        idx = seq.find(guide, idx + 1)
    print('DEBUG: guide occurrences at', occ)
    for pos in occ:
        pam_pos = pos + len(guide)
        print('DEBUG: pam at', pam_pos, 'pam_seq=', seq[pam_pos:pam_pos+3])
