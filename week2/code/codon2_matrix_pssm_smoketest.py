#!/usr/bin/env python3

import codon2_matrix as matrix


def ok(name, cond):
    if cond:
        print("OK "+name)
    else:
        raise Exception("FAIL "+name)


def main():
    counts = {
        'A': [10, 0, 5, 15],
        'C': [0, 20, 0, 0],
        'G': [5, 0, 15, 0],
        'T': [5, 0, 0, 5]
    }
    fpm = matrix.FrequencyPositionMatrix('ACGT', counts)
    pwm = fpm.normalize(pseudocounts=0.1)
    bg = {'A':.25,'C':.25,'G':.25,'T':.25}
    pssm = pwm.log_odds(bg)
    ok('length', pssm.length == 4)
    ok('max>=min', pssm.max >= pssm.min)
    m = pssm.mean(bg)
    s = pssm.std(bg)
    ok('mean finite', m == m)
    ok('std finite', s == s and s >= 0.0)
    # scanning
    score = pssm.calculate('ACGT')
    ok('single score list', hasattr(score, '__len__') and len(score) == 1 and isinstance(score[0], float))
    arr = pssm.calculate('ACGTAC')
    ok('windowed scores', hasattr(arr, '__len__') and len(arr) == 3)
    # bad character -> NaN
    bad = pssm.calculate('ACGN')
    ok('nan list', hasattr(bad, '__len__') and len(bad) == 1 and not (bad[0] == bad[0]))
    print('codon2_matrix PSSM smoketest passed')


if __name__ == '__main__':
    main()


