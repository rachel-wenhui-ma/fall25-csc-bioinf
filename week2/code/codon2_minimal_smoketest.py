#!/usr/bin/env python3
"""
Codon smoketest for codon2_minimal.
Run from this directory (week2/code):
  ~/.codon/bin/codon run codon2_minimal_smoketest.py
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

import codon2_minimal as minimal

def main():
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
    print("codon2_minimal smoketest passed")
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())


