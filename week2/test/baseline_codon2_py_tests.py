#!/usr/bin/env python3
"""
Baseline tests for newly ported codon2_* modules (run under CPython):
- codon2_init (Motif core)
- codon2_matrix
- codon2_minimal
- codon2_thresholds

These mirror baseline_biopython_tests.py and establish a migration baseline
before running under Codon.
"""

import os
import sys
import math
import numpy as np

CODE_DIR = os.path.join(os.path.dirname(__file__), '..', 'code')
sys.path.insert(0, CODE_DIR)

import codon2_matrix as matrix
import codon2_thresholds as thresholds
import codon2_minimal as minimal
import codon2_init as codon2_init

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
Motif = codon2_init.Motif
create = codon2_init.create


def ok(name, cond, detail=None):
    if cond:
        print(f"OK {name}")
    else:
        msg = f"FAIL {name}"
        if detail:
            msg += f": {detail}"
        raise AssertionError(msg)


def test_minimal_parser():
    print("\n=== Codon2(py): MINIMAL parser ===")
    path = os.path.join(DATA_DIR, 'minimal_test.meme')
    with open(path) as fh:
        record = minimal.read(fh)
    ok('record length', len(record) == 3)
    ok('version', record.version in ('4','4.11.2'))
    ok('alphabet', record.alphabet == 'ACGT')
    bg = record.background
    for k, v in [('A',0.303),('C',0.183),('G',0.209),('T',0.306)]:
        ok(f'bg {k}', abs(bg[k]-v) < 1e-3)
    m1 = record[0]
    ok('m1 name', m1.name == 'KRP')
    ok('m1 nsites', m1.num_occurrences == 17)
    ok('m1 length', len(m1) == 19)
    ok('m1 evalue', abs(m1.evalue - 4.1e-9) < 1e-12)
    ok('m1 consensus', str(m1.consensus) == 'TGTGATCGAGGTCACACTT')
    ok('m1 degenerate', str(m1.degenerate_consensus) == 'TGTGANNNWGNTCACAYWW')
    ok('record by name', record['KRP'].name == 'KRP')


def test_matrix_chain_and_scoring():
    print("\n=== Codon2(py): Matrix chain & scoring ===")
    counts = {
        'A': [10, 0, 5, 15],
        'C': [0, 20, 0, 0],
        'G': [5, 0, 15, 0],
        'T': [5, 0, 0, 5]
    }
    fpm = matrix.FrequencyPositionMatrix('ACGT', counts)
    ok('FPM length', fpm.length == 4)
    ok('GC in [0,1]', 0.0 <= fpm.gc_content <= 1.0)
    pwm = fpm.normalize()
    ok('PWM length', pwm.length == 4)
    pssm = pwm.log_odds({'A':.25,'C':.25,'G':.25,'T':.25})
    ok('PSSM length', pssm.length == 4)
    ok('PSSM max >= min', pssm.max >= pssm.min)
    seq = 'ACGTACGT'
    scores = pssm.calculate(seq)
    exp_len = len(seq) - pssm.length + 1
    if exp_len == 1:
        ok('score is float', isinstance(scores, (float, np.floating)))
    else:
        ok('scores length', len(scores) == exp_len)
    scores2 = pssm.calculate(seq.lower())
    if exp_len == 1:
        ok('mixed case float', isinstance(scores2, (float, np.floating)))
    else:
        ok('mixed case same length', len(scores2) == exp_len)
    seq_bad = 'ACGN'
    bad = pssm.calculate(seq_bad)
    ok('bad is NaN (scalar)', math.isnan(float(bad)))


def test_degenerate_and_slicing():
    print("\n=== Codon2(py): Degenerate & slicing ===")
    counts = {
        'A': [15.0, 8.0, 0.0, 10.0],
        'C': [0.0, 2.0, 5.0, 5.0],
        'G': [2.0, 7.0, 15.0, 8.0],
        'T': [3.0, 3.0, 0.0, 0.0]
    }
    m = Motif(alphabet='ACGT', counts=counts)
    deg = str(m.counts.degenerate_consensus)
    ok('degenerate length', len(deg) == 4)
    ok('degenerate codes valid', all(ch in set('ACGTRYSWKMBDHVN') for ch in deg))
    m2 = m[1:-1]
    ok('slice length', len(m2) == len(m)-2)
    ok('slice consensus len', len(str(m2.consensus)) == len(m)-2)


def test_reverse_complement_and_props():
    print("\n=== Codon2(py): reverse_complement & props ===")
    instances = ["ACGT", "ACGG", "ACGA", "ACGT"]
    m = create(instances)
    rc = m.reverse_complement()
    ok('rc same length', len(rc) == len(m))
    for k in 'AT':
        ok(f'rc background {k}', abs(rc.background[k] - 0.25) < 1e-10)
    m.pseudocounts = {'A':1.0,'C':1.0,'G':1.0,'T':1.0}
    rc2 = m.reverse_complement()
    ok('rc2 pseudocount A', abs(rc2.pseudocounts['A'] - 1.0) < 1e-10)


def test_thresholds():
    print("\n=== Codon2(py): thresholds ===")
    counts = {
        'A': [5.0, 1.0, 2.0, 8.0],
        'C': [1.0, 8.0, 1.0, 1.0],
        'G': [2.0, 1.0, 8.0, 1.0],
        'T': [2.0, 1.0, 1.0, 1.0]
    }
    m = Motif(alphabet='ACGT', counts=counts)
    pwm = m.counts.normalize(pseudocounts=0.1)
    bg = {'A':.25,'C':.25,'G':.25,'T':.25}
    pssm = pwm.log_odds(bg)
    dist = thresholds.ScoreDistribution(pssm=pssm, background=bg, precision=50)
    vals = [dist.threshold_fpr(0.01), dist.threshold_fnr(0.1), dist.threshold_balanced(), dist.threshold_patser()]
    for i, v in enumerate(vals):
        ok(f'threshold {i} float', isinstance(v, float))
    ok('range sanity', not any(math.isnan(v) for v in vals))


def main():
    print("Starting Codon2(py) Baseline Tests")
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
    print(f"Completed {passed}/{len(tests)} codon2(py) tests")
    return 0 if passed == len(tests) else 1

if __name__ == '__main__':
    raise SystemExit(main())


