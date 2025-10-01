"""
Ported matrix abstractions (Codon-friendly, no inheritance):
- FrequencyPositionMatrix
- PositionWeightMatrix
- PositionSpecificScoringMatrix
"""

import math


class Seq:
    def __init__(self, sequence: str):
        self.sequence = str(sequence)
    def __str__(self):
        return self.sequence
    def __repr__(self):
        return f"Seq('{self.sequence}')"


def _build_data(alphabet: str, values):
    data = {lt: [] for lt in alphabet}
    length = 0
    for letter in alphabet:
        col = [float(x) for x in values[letter]]
        if length == 0:
            length = len(col)
        elif length != len(col):
            raise ValueError('data has inconsistent lengths')
        data[letter] = col
    return data, length


def _consensus_like(alphabet, data, length, pick_best=True):
    seq = ''
    for i in range(length):
        best = -math.inf if pick_best else math.inf
        ch = ''
        for lt in alphabet:
            v = data[lt][i]
            if pick_best:
                if v > best:
                    best = v
                    ch = lt
            else:
                if v < best:
                    best = v
                    ch = lt
        seq += ch
    return Seq(seq)


def _degenerate(alphabet, data, length):
    code = {
        'A':'A','C':'C','G':'G','T':'T','U':'U',
        'AC':'M','AG':'R','AT':'W','AU':'W','CG':'S','CT':'Y','CU':'Y','GT':'K','GU':'K',
        'ACG':'V','ACT':'H','ACU':'H','AGT':'D','AGU':'D','CGT':'B','CGU':'B',
        'ACGT':'N','ACGU':'N'
    }
    s = ''
    for i in range(length):
        order = sorted(list(alphabet), key=lambda a: data[a][i], reverse=True)
        counts = [data[a][i] for a in order]
        if counts[0] > sum(counts[1:]) and counts[0] > 2*counts[1]:
            key = order[0]
        elif 4*sum(counts[:2]) > 3*sum(counts):
            key = ''.join(sorted(order[:2]))
        elif len(counts) > 3 and counts[3] == 0:
            key = ''.join(sorted(order[:3]))
        else:
            key = ''.join(sorted(alphabet))
        s += code.get(key, key)
    return Seq(s)


class FrequencyPositionMatrix:
    def __init__(self, alphabet: str, values):
        # declare attributes to satisfy Codon typechecker
        self.alphabet = ''
        self.length = 0
        self.data = {'A': [], 'C': [], 'G': [], 'T': [], 'U': []}
        self.alphabet = alphabet
        self.data, self.length = _build_data(alphabet, values)

    def get_row(self, letter):
        return self.data[letter]

    @property
    def consensus(self):
        return _consensus_like(self.alphabet, self.data, self.length, True)

    @property
    def anticonsensus(self):
        return _consensus_like(self.alphabet, self.data, self.length, False)

    @property
    def degenerate_consensus(self):
        return _degenerate(self.alphabet, self.data, self.length)

    @property
    def gc_content(self):
        total = 0.0
        gc = 0.0
        for i in range(self.length):
            for lt in self.alphabet:
                v = self.data[lt][i]
                total += v
                if lt in ('G','C'):
                    gc += v
        return gc/total if total>0 else 0.0

    def reverse_complement(self):
        values = {}
        if self.alphabet == 'ACGU':
            values['A'] = self.data['U'][::-1]
            values['U'] = self.data['A'][::-1]
        else:
            values['A'] = self.data['T'][::-1]
            values['T'] = self.data['A'][::-1]
        values['C'] = self.data['G'][::-1]
        values['G'] = self.data['C'][::-1]
        return FrequencyPositionMatrix(self.alphabet, values)

    def normalize(self, pseudocounts = None):
        counts = {}
        if pseudocounts is None:
            for lt in self.alphabet:
                counts[lt] = [0.0]*self.length
        elif isinstance(pseudocounts, dict):
            for lt in self.alphabet:
                counts[lt] = [float(pseudocounts[lt])]*self.length
        else:
            for lt in self.alphabet:
                counts[lt] = [float(pseudocounts)]*self.length
        for i in range(self.length):
            for lt in self.alphabet:
                counts[lt][i] += self.data[lt][i]
        return PositionWeightMatrix(self.alphabet, counts)


class PositionWeightMatrix:
    def __init__(self, alphabet: str, values):
        # declare attributes to satisfy Codon typechecker
        self.alphabet = ''
        self.length = 0
        self.data = {'A': [], 'C': [], 'G': [], 'T': [], 'U': []}
        self.alphabet = alphabet
        self.data, self.length = _build_data(alphabet, values)
        for i in range(self.length):
            total = 0.0
            for lt in self.alphabet:
                total += self.data[lt][i]
            for lt in self.alphabet:
                self.data[lt][i] = (self.data[lt][i] / total) if total>0 else 0.0

    @property
    def consensus(self):
        return _consensus_like(self.alphabet, self.data, self.length, True)

    @property
    def anticonsensus(self):
        return _consensus_like(self.alphabet, self.data, self.length, False)

    @property
    def degenerate_consensus(self):
        return _degenerate(self.alphabet, self.data, self.length)

    def log_odds(self, background = None):
        if background is None:
            background = {lt:1.0 for lt in self.alphabet}
        total = 0.0
        for v in background.values():
            total += v
        bg = {k:(v/total) for k,v in background.items()}
        values = {lt: [] for lt in self.alphabet}
        for i in range(self.length):
            for lt in self.alphabet:
                b = bg[lt]
                p = self.data[lt][i]
                if b>0:
                    values[lt].append(math.log(p/b, 2) if p>0 else -math.inf)
                else:
                    values[lt].append(math.inf if p>0 else math.nan)
        return PositionSpecificScoringMatrix(self.alphabet, values)


class PositionSpecificScoringMatrix:
    def __init__(self, alphabet: str, values):
        # declare attributes to satisfy Codon typechecker
        self.alphabet = ''
        self.length = 0
        self.data = {'A': [], 'C': [], 'G': [], 'T': [], 'U': []}
        self.alphabet = alphabet
        self.data, self.length = _build_data(alphabet, values)

    def at_column(self, pos: int):
        return {lt: self.data[lt][pos] for lt in self.alphabet}

    def letter_scores_at(self, pos: int):
        return {lt: self.data[lt][pos] for lt in self.alphabet}

    def calculate(self, sequence):
        if sorted(self.alphabet) != ['A','C','G','T']:
            raise ValueError(f"PSSM has wrong alphabet: {self.alphabet} - Use only with DNA motifs")
        if isinstance(sequence, str):
            # Codon strings may not have .encode; convert to list of ASCII codes
            seq_bytes = []
            for ch in sequence:
                c = ord(ch)
                if c >= 128:
                    raise ValueError('sequence should contain ASCII characters only')
                seq_bytes.append(c)
        else:
            # assume an iterable of ints/bytes-like
            seq_bytes = list(sequence)
        n = len(seq_bytes)
        m = self.length
        # build dense columns for fast access
        logodds = []
        for i in range(m):
            row = [0.0, 0.0, 0.0, 0.0]
            row[0] = self.data['A'][i]
            row[1] = self.data['C'][i]
            row[2] = self.data['G'][i]
            row[3] = self.data['T'][i]
            logodds.append(row)
        def base_index(b: int) -> int:
            if b in (65,97): return 0
            if b in (67,99): return 1
            if b in (71,103): return 2
            if b in (84,116): return 3
            return -1
        if n == m:
            s = 0.0
            bad = False
            for j in range(m):
                idx = base_index(seq_bytes[j])
                if idx < 0:
                    bad = True
                    break
                s += logodds[j][idx]
            return [float('nan')] if bad else [s]
        scores = []
        for i in range(n-m+1):
            s = 0.0
            bad = False
            for j in range(m):
                idx = base_index(seq_bytes[i+j])
                if idx < 0:
                    bad = True
                    break
                s += logodds[j][idx]
            scores.append(float('nan') if bad else s)
        return scores

    @property
    def max(self):
        score = 0.0
        for i in range(self.length):
            best = -math.inf
            for lt in self.alphabet:
                v = self.data[lt][i]
                if v > best:
                    best = v
            score += best
        return score

    @property
    def min(self):
        score = 0.0
        for i in range(self.length):
            worst = math.inf
            for lt in self.alphabet:
                v = self.data[lt][i]
                if v < worst:
                    worst = v
            score += worst
        return score

    @property
    def gc_content(self):
        raise Exception('Cannot compute the %GC composition of a PSSM')

    def mean(self, background = None) -> float:
        if background is None:
            background = {lt:1.0 for lt in self.alphabet}
        total = 0.0
        for v in background.values():
            total += v
        bg = {k:(v/total) for k,v in background.items()}
        sx = 0.0
        for i in range(self.length):
            for lt in self.alphabet:
                lo = self.data[lt][i]
                if math.isnan(lo) or (math.isinf(lo) and lo<0):
                    continue
                b = bg[lt]
                p = b * (2 ** lo)
                sx += p * lo
        return sx

    def std(self, background = None) -> float:
        if background is None:
            background = {lt:1.0 for lt in self.alphabet}
        total = 0.0
        for v in background.values():
            total += v
        bg = {k:(v/total) for k,v in background.items()}
        variance = 0.0
        for i in range(self.length):
            sx = 0.0
            sxx = 0.0
            for lt in self.alphabet:
                lo = self.data[lt][i]
                if math.isnan(lo) or (math.isinf(lo) and lo<0):
                    continue
                b = bg[lt]
                p = b * (2 ** lo)
                sx += p * lo
                sxx += p * lo * lo
            sxx -= sx * sx
            variance += sxx
        return math.sqrt(max(variance, 0.0))
