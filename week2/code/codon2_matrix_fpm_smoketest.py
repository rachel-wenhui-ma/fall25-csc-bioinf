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
    ok('length', fpm.length == 4)
    gc = fpm.gc_content
    ok('gc in [0,1]', 0.0 <= gc <= 1.0)
    rc = fpm.reverse_complement()
    ok('rc length', rc.length == 4)
    ok('consensus len', len(str(fpm.consensus)) == 4)
    ok('degenerate len', len(str(fpm.degenerate_consensus)) == 4)
    print('codon2_matrix FPM smoketest passed')


if __name__ == '__main__':
    main()


