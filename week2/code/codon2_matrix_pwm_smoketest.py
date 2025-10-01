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
    ok('length', pwm.length == 4)
    # each column sums to ~1.0
    for i in range(pwm.length):
        s = pwm.data['A'][i] + pwm.data['C'][i] + pwm.data['G'][i] + pwm.data['T'][i]
        ok(f'col {i} sums to 1', abs(s - 1.0) < 1e-6)
    ok('consensus len', len(str(pwm.consensus)) == 4)
    print('codon2_matrix PWM smoketest passed')


if __name__ == '__main__':
    main()


