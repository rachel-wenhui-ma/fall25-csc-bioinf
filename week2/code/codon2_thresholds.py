"""
Ported thresholds: ScoreDistribution with approximate convolution scheme.
"""
import math

class ScoreDistribution:
    def __init__(self, motif=None, precision: int = 10**3, pssm=None, background = None):
        # Initialize fields to keep Codon typechecker happy
        self.n_points = 0
        self.min_score = 0.0
        self.interval = 0.0
        self.step = 1.0
        self.ic = 0.0
        if pssm is None:
            raise ValueError('This pared-down port expects pssm provided')
        self.min_score = min(0.0, pssm.min)
        self.interval = max(0.0, pssm.max) - self.min_score
        self.n_points = max(2, precision * pssm.length)
        if self.n_points > 1 and self.interval > 0.0:
            self.step = self.interval / (self.n_points - 1)
        else:
            # Ensure positive, non-zero step to avoid division by zero
            self.interval = 1.0 if self.interval <= 0.0 else self.interval
            self.step = 1.0
        bg_mean = background if background is not None else {k:1.0 for k in pssm.alphabet}
        self.ic = pssm.mean(bg_mean)
        # densities
        self.mo_density = [0.0]*self.n_points
        self.bg_density = [0.0]*self.n_points
        z = -self._index_diff(self.min_score)
        if 0 <= z < self.n_points:
            self.mo_density[z] = 1.0
            self.bg_density[z] = 1.0
        # DP accumulate
        bg = background if background is not None else {k:1.0 for k in pssm.alphabet}
        total = sum(bg.values())
        bg = {k:v/total for k,v in bg.items()}
        for pos in range(pssm.length):
            # use explicit accessor to avoid __getitem__ overloads
            try:
                lo = pssm.at_column(pos)
            except Exception:
                lo = pssm.letter_scores_at(pos)
            mo_new = [0.0]*self.n_points
            bg_new = [0.0]*self.n_points
            for letter, score in lo.items():
                b = bg[letter]
                if math.isinf(score) and score < 0:
                    mo = 0.0
                elif math.isinf(score) and score > 0:
                    mo = 1.0
                elif math.isnan(score):
                    mo = b
                else:
                    mo = (2 ** score) * b
                d = self._index_diff(score)
                for i in range(self.n_points):
                    j = self._add(i, d)
                    mo_new[j] += self.mo_density[i] * mo
                    bg_new[j] += self.bg_density[i] * b
            self.mo_density = mo_new
            self.bg_density = bg_new

    def _index_diff(self, x: float, y: float = 0.0) -> int:
        if math.isnan(x) or math.isnan(y):
            return 0
        if math.isinf(x):
            return self.n_points-1 if x>0 else 0
        if self.step <= 0.0:
            return 0
        return int((x - y + 0.5*self.step) // self.step)

    def _add(self, i: int, j: int) -> int:
        if i+j < 0:
            return 0
        if i+j >= self.n_points:
            return self.n_points-1
        return i+j

    def threshold_fpr(self, fpr: float) -> float:
        i = self.n_points-1
        p = 0.0
        while i>=0 and p < fpr:
            p += self.bg_density[i]
            i -= 1
        i = max(0, i)
        return self.min_score + i*self.step

    def threshold_fnr(self, fnr: float) -> float:
        i = 0
        p = 0.0
        while i<self.n_points and p < fnr:
            p += self.mo_density[i]
            i += 1
        i = min(self.n_points-1, i)
        return self.min_score + i*self.step

    def threshold_balanced(self, rate_proportion: float = 1.0):
        i = self.n_points-1
        fpr = 0.0
        fnr = 1.0
        while i>=0 and fpr*rate_proportion < fnr:
            fpr += self.bg_density[i]
            fnr -= self.mo_density[i]
            i -= 1
        i = max(0, i)
        val = self.min_score + i*self.step
        return val

    def threshold_balanced_with_rate(self, rate_proportion: float = 1.0):
        i = self.n_points-1
        fpr = 0.0
        fnr = 1.0
        while i>=0 and fpr*rate_proportion < fnr:
            fpr += self.bg_density[i]
            fnr -= self.mo_density[i]
            i -= 1
        i = max(0, i)
        val = self.min_score + i*self.step
        return (val, fpr)

    def threshold_patser(self) -> float:
        return self.threshold_fpr(fpr=2**(-self.ic))
