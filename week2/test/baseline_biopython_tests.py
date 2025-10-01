#!/usr/bin/env python3
"""
Baseline tests against original BioPython implementation for four modules:
- Bio.motifs.__init__ (Motif core)
- Bio.motifs.matrix
- Bio.motifs.minimal
- Bio.motifs.thresholds

This file runs only with Python + BioPython installed.
It establishes expected behavior and numbers to use as migration baseline.
"""

import os
import math

from Bio import motifs
from Bio.motifs import matrix as bio_matrix
from Bio.motifs import thresholds as bio_thresholds
from Bio.motifs import minimal as bio_minimal
from Bio.Seq import Seq
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')


def ok(name, cond, detail=None):
    if cond:
        print(f"OK {name}")
    else:
        msg = f"FAIL {name}"
        if detail:
            msg += f": {detail}"
        raise AssertionError(msg)


def test_minimal_parser():
    print("\n=== Baseline: MINIMAL parser ===")
    path = os.path.join(DATA_DIR, 'minimal_test.meme')
    with open(path) as fh:
        record = motifs.parse(fh, 'minimal')
    ok('record length', len(record) == 3, f"got {len(record)}")
    ok('version', record.version == '4')
    ok('alphabet', record.alphabet == 'ACGT')
    bg = record.background
    ok('bg A', abs(bg['A'] - 0.303) < 1e-3)
    ok('bg C', abs(bg['C'] - 0.183) < 1e-3)
    ok('bg G', abs(bg['G'] - 0.209) < 1e-3)
    ok('bg T', abs(bg['T'] - 0.306) < 1e-3)
    m1 = record[0]
    ok('m1 name', m1.name == 'KRP')
    ok('m1 nsites', m1.num_occurrences == 17)
    ok('m1 length', len(m1) == 19)
    ok('m1 evalue', abs(m1.evalue - 4.1e-9) < 1e-12)
    ok('m1 consensus', str(m1.consensus) == 'TGTGATCGAGGTCACACTT')
    ok('m1 degenerate', str(m1.degenerate_consensus) == 'TGTGANNNWGNTCACAYWW')
    ok('record by name', record['KRP'].name == 'KRP')


def test_matrix_chain_and_scoring():
    print("\n=== Baseline: Matrix chain (FPM→PWM→PSSM) and scoring ===")
    # SRF motif from PFM file
    path = os.path.join(DATA_DIR, 'SRF.pfm')
    with open(path) as fh:
        m = motifs.read(fh, 'pfm')
    fpm = m.counts
    ok('FPM length', fpm.length == len(m))
    # GC content simple sanity (value depends on this matrix)
    gc = fpm.gc_content
    ok('GC in [0,1]', 0.0 <= gc <= 1.0)
    # PWM and PSSM
    pwm = fpm.normalize()
    ok('PWM length', pwm.length == fpm.length)
    pssm = pwm.log_odds({'A':0.25,'C':0.25,'G':0.25,'T':0.25})
    ok('PSSM length', pssm.length == fpm.length)
    # PSSM max/min sanity
    ok('PSSM max >= min', pssm.max >= pssm.min)
    # scoring
    seq = 'ACGTACGTACGT'
    scores = pssm.calculate(seq)
    exp_len = len(seq) - pssm.length + 1
    if exp_len == 1:
        ok('score is float', isinstance(scores, (float, np.floating)))
    else:
        ok('scores length', len(scores) == exp_len)
    # mixed case
    scores2 = pssm.calculate(seq.lower())
    if exp_len == 1:
        ok('mixed case float', isinstance(scores2, (float, np.floating)))
    else:
        ok('mixed case same length', len(scores2) == exp_len)
    # bad chars give NaN at positions
    seq_bad = 'ACGN' * max(1, pssm.length // 4)
    while len(seq_bad) < pssm.length:
        seq_bad += 'N'
    bad_scores = pssm.calculate(seq_bad)
    if len(seq_bad) - pssm.length + 1 == 1:
        ok('bad scalar is NaN', math.isnan(float(bad_scores)))
    else:
        ok('bad returns array', hasattr(bad_scores, '__len__'))
        ok('has NaN', any(math.isnan(float(x)) for x in bad_scores))


def test_degenerate_and_slicing():
    print("\n=== Baseline: Degenerate consensus and slicing ===")
    counts = {
        'A': [15.0, 8.0, 0.0, 10.0],
        'C': [0.0, 2.0, 5.0, 5.0],
        'G': [2.0, 7.0, 15.0, 8.0],
        'T': [3.0, 3.0, 0.0, 0.0]
    }
    m = motifs.Motif(alphabet='ACGT', counts=counts)
    fpm = m.counts
    deg = str(fpm.degenerate_consensus)
    ok('degenerate length', len(deg) == 4)
    ok('degenerate codes valid', all(ch in set('ACGTRYSWKMBDHVN') for ch in deg))
    # slicing on Motif
    m2 = m[1:-1]
    ok('slice length', len(m2) == len(m)-2)
    ok('slice consensus length', len(str(m2.consensus)) == len(m)-2)


def test_reverse_complement_and_props():
    print("\n=== Baseline: reverse_complement & properties ===")
    instances = ["ACGT", "ACGG", "ACGA", "ACGT"]
    m = motifs.create(instances)
    rc = m.reverse_complement()
    ok('rc same length', len(rc) == len(m))
    # background default uniform
    for k in 'AT':
        ok(f'rc background {k}', abs(rc.background[k] - 0.25) < 1e-10)
    # pseudocounts mapping when set
    m.pseudocounts = {'A':1.0,'C':1.0,'G':1.0,'T':1.0}
    rc2 = m.reverse_complement()
    ok('rc2 pseudocount A', abs(rc2.pseudocounts['A'] - 1.0) < 1e-10)


def test_thresholds():
    print("\n=== Baseline: thresholds ===")
    # Use a small stable matrix to avoid infinities
    counts = {
        'A': [5.0, 1.0, 2.0, 8.0],
        'C': [1.0, 8.0, 1.0, 1.0],
        'G': [2.0, 1.0, 8.0, 1.0],
        'T': [2.0, 1.0, 1.0, 1.0]
    }
    m = motifs.Motif(alphabet='ACGT', counts=counts)
    pwm = m.counts.normalize(pseudocounts=0.1)
    bg = {'A':0.25,'C':0.25,'G':0.25,'T':0.25}
    pssm = pwm.log_odds(bg)
    dist = bio_thresholds.ScoreDistribution(pssm=pssm, background=bg, precision=50)
    fpr_th = dist.threshold_fpr(0.01)
    fnr_th = dist.threshold_fnr(0.1)
    bal_th = dist.threshold_balanced()
    patser_th = dist.threshold_patser()
    for name, v in [('fpr',fpr_th),('fnr',fnr_th),('bal',bal_th),('patser',patser_th)]:
        ok(f'{name} is float', isinstance(v, float))
    ok('range sanity', not math.isnan(fpr_th) and not math.isnan(bal_th))


def main():
    print("Starting Baseline BioPython Tests")
    print("="*60)
    tests = [
        test_minimal_parser,
        test_matrix_chain_and_scoring,
        test_degenerate_and_slicing,
        test_reverse_complement_and_props,
        test_thresholds,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(str(e))
            break
    print("\n"+"="*60)
    print(f"Completed {passed}/{len(tests)} baseline tests")
    return 0 if passed == len(tests) else 1

if __name__ == '__main__':
    raise SystemExit(main())
