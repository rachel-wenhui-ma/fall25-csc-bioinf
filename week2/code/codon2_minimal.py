"""
Minimal MEME format reader (Codon-friendly, no typing generics).
"""

try:
    from .codon2_init import Motif  # package context
except Exception:  # script context
    from codon2_init import Motif

class Record:
    def __init__(self):
        # seed with a typed dummy motif so Codon infers List[Motif]
        dummy_counts = {'A':[0.0], 'C':[0.0], 'G':[0.0], 'T':[0.0]}
        try:
            dummy = Motif(alphabet='ACGT', counts=dummy_counts)
        except Exception:
            dummy = None
        self._items = [dummy]
        self.version = ''
        self.alphabet = ''
        # Seed with typed keys/values so Codon infers Dict[str,float]
        self.background = {'A': 0.0, 'C': 0.0, 'G': 0.0, 'T': 0.0, 'U': 0.0}
        self.datafile = ''
        self.command = ''
    def __len__(self):
        n = len(self._items) - 1
        return n if n >= 0 else 0
    def __iter__(self):
        return iter(self._items[1:])
    def __getitem__(self, key):
        if isinstance(key, str):
            for m in self._items[1:]:
                try:
                    n = m.name
                except Exception:
                    continue
                if n == key:
                    return m
            raise KeyError(key)
        # integer index, skipping dummy at 0
        try:
            i = int(key)
        except Exception:
            raise IndexError('record index out of range')
        if 0 <= i < (len(self._items)-1):
            return self._items[i+1]
        raise IndexError('record index out of range')
    def append(self, item):
        self._items.append(item)

def _read_version(record, it, idx):
    while idx < len(it):
        line = it[idx].strip()
        if line.startswith('MEME version'):
            record.version = line.split()[-1]
            return idx+1
        idx += 1
    raise ValueError('MEME version not found')

def _read_alphabet(record, it, idx):
    while idx < len(it):
        line = it[idx].strip()
        if line.startswith('ALPHABET'):
            val = line.replace('ALPHABET=','').strip()
            record.alphabet = val
            return idx+1
        idx += 1
    raise ValueError('ALPHABET not found')

def _read_background(record, it, idx):
    # find header
    while idx < len(it):
        line = it[idx].strip()
        if line.startswith('Background letter frequencies'):
            idx += 1
            break
        idx += 1
    bg = []
    while idx < len(it):
        line = it[idx].strip()
        if not line:
            break
        parts = line.split()
        for j, tok in enumerate(parts):
            if j % 2 == 1:  # value
                bg.append(float(tok))
        idx += 1
    if record.alphabet == 'ACGT':
        record.background = dict(zip('ACGT', bg))
    elif record.alphabet == 'ACGU':
        record.background = dict(zip('ACGU', bg))
    else:
        raise ValueError('Only DNA/RNA supported')
    return idx+1

def _read_motif_statistics(it, idx):
    # returns: next_idx, length, nsites, evalue
    while idx < len(it):
        line = it[idx].strip()
        if line.startswith('letter-probability matrix:'):
            break
        idx += 1
    text = it[idx]
    def _get(key, default):
        return float(text.split(key+'=')[1].split()[0]) if (key+'=') in text else default
    length = int(_get('w', 0))
    nsites = int(_get('nsites', 20))
    evalue = float(_get('E', 0.0))
    return idx+1, length, nsites, evalue

def _read_lpm(record, it, idx, length, nsites):
    # Avoid dict lookups within the hot loop; build arrays then dict
    letters = record.alphabet
    a = [0]*length
    b = [0]*length
    c = [0]*length
    d = [0]*length
    pos = 0
    while idx < len(it) and pos < length:
        line = it[idx].strip()
        if not line:
            break
        parts = line.split()
        if len(parts) != 4:
            break
        v0 = int(round(float(parts[0])*nsites))
        v1 = int(round(float(parts[1])*nsites))
        v2 = int(round(float(parts[2])*nsites))
        v3 = int(round(float(parts[3])*nsites))
        a[pos] = v0
        b[pos] = v1
        c[pos] = v2
        d[pos] = v3
        pos += 1
        idx += 1
    counts = {
        letters[0]: a,
        letters[1]: b,
        letters[2]: c,
        letters[3]: d,
    }
    return idx, counts

def read(handle):
    lines = handle.readlines()
    idx = 0
    record = Record()
    idx = _read_version(record, lines, idx)
    idx = _read_alphabet(record, lines, idx)
    idx = _read_background(record, lines, idx)
    # motifs
    while idx < len(lines):
        # find MOTIF line
        while idx < len(lines) and not lines[idx].startswith('MOTIF'):
            idx += 1
        if idx >= len(lines):
            break
        name = lines[idx].split()[1]
        idx, length, nsites, evalue = _read_motif_statistics(lines, idx+1)
        idx, counts = _read_lpm(record, lines, idx, length, nsites)
        m = Motif(alphabet=record.alphabet, counts=counts)
        m.background = record.background
        m.length = m.counts.length
        m.num_occurrences = nsites
        m.evalue = evalue
        m.name = name
        record.append(m)
    return record
