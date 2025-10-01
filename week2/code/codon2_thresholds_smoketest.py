#!/usr/bin/env python3
"""
Codon smoketest for codon2_thresholds.
Run from this directory (week2/code):
  ~/.codon/bin/codon run codon2_thresholds_smoketest.py
"""

def ok(name, cond, detail=None):
    if cond:
        print("OK "+name)
    else:
        msg = "FAIL "+name
        if detail:
            msg += ": "+str(detail)
        print(msg)
        raise Exception(msg)

import codon2_init as codon2_init
import codon2_thresholds as thresholds

def main():
    counts = {
        'A': [5.0, 1.0, 2.0, 8.0],
        'C': [1.0, 8.0, 1.0, 1.0],
        'G': [2.0, 1.0, 8.0, 1.0],
        'T': [2.0, 1.0, 1.0, 1.0]
    }
    m = codon2_init.Motif(alphabet='ACGT', counts=counts)
    print("building pwm...")
    pwm = m.counts.normalize(pseudocounts=0.1)
    bg = {'A':.25,'C':.25,'G':.25,'T':.25}
    print("building pssm...")
    pssm = pwm.log_odds(bg)
    print("building distribution...")
    dist = thresholds.ScoreDistribution(pssm=pssm, background=bg, precision=50)
    print("computing thresholds...")
    vals = []
    print("- fpr")
    vals.append(dist.threshold_fpr(0.01))
    print("- fnr")
    vals.append(dist.threshold_fnr(0.1))
    print("- balanced")
    vals.append(dist.threshold_balanced())
    print("- patser")
    vals.append(dist.threshold_patser())
    for i, v in enumerate(vals):
        ok('threshold '+str(i)+' float', isinstance(v, float))
    ok('range sanity', not any((v != v) for v in vals))
    print("codon2_thresholds smoketest passed")
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())


