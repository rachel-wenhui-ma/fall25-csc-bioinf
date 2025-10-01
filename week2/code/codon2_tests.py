#!/usr/bin/env python3
"""
Codon-friendly test runner for codon2_* modules.
Run from this directory (week2/code):
  ~/.codon/bin/codon run codon2_tests.py
"""

# Avoid heavy stdlib; keep to basic builtins

def ok(name, cond, detail=None):
    if cond:
        print("OK "+name)
    else:
        msg = "FAIL "+name
        if detail:
            msg += ": "+str(detail)
        print(msg)
        raise Exception(msg)

# Imports (modules are in the same folder)
import codon2_matrix as matrix
import codon2_thresholds as thresholds
import codon2_minimal as minimal
import codon2_init as codon2_init

Motif = codon2_init.Motif
create = codon2_init.create


def test_minimal_parser():
    print("\n=== Codon2(Codon): MINIMAL parser ===")
    path = "../data/minimal_test.meme"
    with open(path, "r") as fh:
        record = minimal.read(fh)
    ok('record length', len(record) == 3)
    ok('version', record.version in ('4','4.11.2'))
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
    print("\n=== Codon2(Codon): Matrix chain & scoring ===")
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
        ok('score scalar or [scalar]', isinstance(scores, float) or (hasattr(scores, '__len__') and len(scores) == 1))
    else:
        ok('scores length', len(scores) == exp_len)
    scores2 = pssm.calculate(seq.lower())
    if exp_len == 1:
        ok('mixed case scalar or [scalar]', isinstance(scores2, float) or (hasattr(scores2, '__len__') and len(scores2) == 1))
    else:
        ok('mixed case same length', len(scores2) == exp_len)
    # bad char -> NaN
    seq_bad = 'ACGN'
    bad = pssm.calculate(seq_bad)
    # In scalar case, allow float NaN or [NaN]
    if isinstance(bad, float):
        ok('bad is NaN (scalar)', not (bad == bad))
    else:
        ok('bad is [NaN] (scalar)', hasattr(bad, '__len__') and len(bad) == 1 and not (bad[0] == bad[0]))


def test_degenerate_and_slicing():
    print("\n=== Codon2(Codon): Degenerate & slicing ===")
    counts = {
        'A': [15.0, 8.0, 0.0, 10.0],
        'C': [0.0, 2.0, 5.0, 5.0],
        'G': [2.0, 7.0, 15.0, 8.0],
        'T': [3.0, 3.0, 0.0, 0.0]
    }
    m = Motif(alphabet='ACGT', counts=counts)
    deg = str(m.counts.degenerate_consensus)
    valid = 'ACGTRYSWKMBDHVN'
    ok('degenerate length', len(deg) == 4)
    ok('degenerate codes valid', all(ch in valid for ch in deg))
    m2 = m[1:-1]
    ok('slice length', len(m2) == len(m)-2)
    ok('slice consensus len', len(str(m2.consensus)) == len(m)-2)


def test_reverse_complement_and_props():
    print("\n=== Codon2(Codon): reverse_complement & props ===")
    instances = ["ACGT", "ACGG", "ACGA", "ACGT"]
    m = create(instances)
    rc = m.reverse_complement()
    ok('rc same length', len(rc) == len(m))
    ok('rc background A', abs(rc.background['A'] - 0.25) < 1e-10)
    ok('rc background T', abs(rc.background['T'] - 0.25) < 1e-10)
    m.pseudocounts = {'A':1.0,'C':1.0,'G':1.0,'T':1.0}
    rc2 = m.reverse_complement()
    ok('rc2 pseudocount A', abs(rc2.pseudocounts['A'] - 1.0) < 1e-10)


def test_thresholds():
    print("\n=== Codon2(Codon): thresholds ===")
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
        ok('threshold '+str(i)+' float', isinstance(v, float))
    # no NaN
    ok('range sanity', not any((v != v) for v in vals))


def main():
    print("Starting Codon2(Codon) Tests")
    print("="*60)
    passed = 0
    total = 5
    try:
        test_minimal_parser()
        passed += 1
    except Exception as e:
        print(str(e))
        print("Aborting after failure in test_minimal_parser")
        print("\n"+"="*60)
        print("Completed "+str(passed)+"/"+str(total)+" Codon tests")
        return 1
    try:
        test_matrix_chain_and_scoring()
        passed += 1
    except Exception as e:
        print(str(e))
        print("Aborting after failure in test_matrix_chain_and_scoring")
        print("\n"+"="*60)
        print("Completed "+str(passed)+"/"+str(total)+" Codon tests")
        return 1
    try:
        test_degenerate_and_slicing()
        passed += 1
    except Exception as e:
        print(str(e))
        print("Aborting after failure in test_degenerate_and_slicing")
        print("\n"+"="*60)
        print("Completed "+str(passed)+"/"+str(total)+" Codon tests")
        return 1
    try:
        test_reverse_complement_and_props()
        passed += 1
    except Exception as e:
        print(str(e))
        print("Aborting after failure in test_reverse_complement_and_props")
        print("\n"+"="*60)
        print("Completed "+str(passed)+"/"+str(total)+" Codon tests")
        return 1
    try:
        test_thresholds()
        passed += 1
    except Exception as e:
        print(str(e))
        print("Aborting after failure in test_thresholds")
        print("\n"+"="*60)
        print("Completed "+str(passed)+"/"+str(total)+" Codon tests")
        return 1
    print("\n"+"="*60)
    print("Completed "+str(passed)+"/"+str(total)+" Codon tests")
    return 0 if passed == total else 1

if __name__ == '__main__':
    import sys
    sys.exit(main())


