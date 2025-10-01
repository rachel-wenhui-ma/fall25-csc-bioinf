"""
Ported __init__ functionality (Codon-friendly): Motif core and integration with codon2_matrix.
"""

import math
import codon2_matrix as matrix

class Motif:
    def __init__(self, alphabet: str = 'ACGT', alignment = None, counts = None):
        if counts is not None and alignment is not None:
            raise ValueError('Specify either counts or an alignment, do not specify both')
        self.name: str = ''
        # fields that some parsers populate; declare to satisfy Codon
        self.num_occurrences: int = 0
        self.evalue: float = 0.0
        self.alphabet: str = alphabet
        # Always keep concrete dicts with full alphabet to satisfy Codon typing
        letters = ['A','C','G'] + (['T'] if 'T' in alphabet else ['U'])
        self.pseudocounts = {k: 0.0 for k in letters}
        self.background = {k: (1.0/len(letters)) for k in letters}
        self.mask = None
        if counts is not None:
            self.alignment = None
            # use codon2_matrix for frequency matrix
            self.counts = matrix.FrequencyPositionMatrix(alphabet, counts)
            self.length = self.counts.length
        elif alignment is not None:
            self.alignment = alignment
            length = len(alignment[0]) if alignment else 0
            freqs = {ch: [0.0]*length for ch in alphabet}
            for seq in alignment:
                for i, ch in enumerate(seq):
                    if ch in freqs:
                        freqs[ch][i] += 1.0
            self.counts = matrix.FrequencyPositionMatrix(alphabet, freqs)
            self.length = length
        else:
            self.alignment = None
            self.counts = None
            self.length = 0
        # defaults already set above

    def __len__(self):
        return self.length

    def __getitem__(self, key):
        if not isinstance(key, slice):
            raise TypeError('motif indices must be slices')
        if self.alignment is None:
            if self.counts is None:
                new_counts = None
            else:
                new_counts = {ch: self.counts.get_row(ch)[key] for ch in self.alphabet}
            m = Motif(alphabet=self.alphabet, counts=new_counts)
        else:
            new_align = [seq[key] for seq in self.alignment]
            m = Motif(alphabet=self.alphabet, alignment=new_align)
        m.pseudocounts = self.pseudocounts.copy()
        m.background = self.background.copy()
        return m

    @property
    def pwm(self):
        return self.counts.normalize(self.pseudocounts)

    @property
    def pssm(self):
        return self.pwm.log_odds(self.background)

    @property
    def consensus(self):
        return self.counts.consensus

    @property
    def anticonsensus(self):
        return self.counts.anticonsensus

    @property
    def degenerate_consensus(self):
        return self.counts.degenerate_consensus

    @property
    def relative_entropy(self):
        bg = self.background or {ch: 0.25 for ch in ('A','C','G','T')}
        pc = self.pseudocounts or {ch: 0.0 for ch in bg}
        values = [0.0]*self.length
        total = [sum(self.counts[ch][i] + pc.get(ch,0.0) for ch in self.alphabet) for i in range(self.length)]
        for ch in self.alphabet:
            c = [(self.counts[ch][i] + pc.get(ch,0.0)) for i in range(self.length)]
            for i in range(self.length):
                if c[i] > 0 and total[i] > 0:
                    p = c[i] / total[i]
                    values[i] += p * math.log(p / bg[ch], 2)
        return values

    def reverse_complement(self):
        alpha = self.alphabet
        if set(alpha) not in (set('ACGT'), set('ACGU')):
            raise ValueError('Calculating reverse complement only works for DNA and RNA motifs')
        if self.alignment is not None:
            comp = {'A':'T','T':'A','C':'G','G':'C','U':'A'}
            rc_align = []
            for s in self.alignment:
                rc_align.append(''.join(comp.get(ch,ch) for ch in reversed(s)))
            res = Motif(alphabet=alpha, alignment=rc_align)
        else:
            T_or_U = 'T' if 'T' in alpha else 'U'
            counts = {
                'A': self.counts.get_row(T_or_U)[::-1],
                'C': self.counts.get_row('G')[::-1],
                'G': self.counts.get_row('C')[::-1],
                T_or_U: self.counts.get_row('A')[::-1]
            }
            res = Motif(alphabet=alpha, counts=counts)
        # map background/pseudocounts
        bg = self.background
        t_or_u = 'T' if 'T' in alpha else 'U'
        res.background = {
            'A': bg.get(t_or_u, 0.0),
            'C': bg.get('G', 0.0),
            'G': bg.get('C', 0.0),
            t_or_u: bg.get('A', 0.0)
        }
        pc = self.pseudocounts
        res.pseudocounts = {
            'A': pc.get(t_or_u, 0.0),
            'C': pc.get('G', 0.0),
            'G': pc.get('C', 0.0),
            t_or_u: pc.get('A', 0.0)
        }
        return res


def create(instances, alphabet: str = 'ACGT'):
    return Motif(alphabet=alphabet, alignment=instances)

# read/parse minimal stub: baseline tests直接使用 codon2_minimal.read
