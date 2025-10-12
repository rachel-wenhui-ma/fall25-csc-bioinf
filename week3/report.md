# Python to Codon Migration Report: Phylogenetic Tree Algorithms

## Major Challenges Encountered

### 1. Strict Type System

**Problem**: Codon's type system is significantly stricter than Python's, requiring explicit type annotations and disallowing many dynamic typing features.

**Specific Issues**:
- `List[int]` and `List[float]` incompatibility
- `Optional[NoneType]` vs `Optional[int]` type mismatches
- No support for `Any` type

**Solution**: 
- Careful type annotation design
- Unified use of `np.float64` for all floating-point operations
- Explicit handling of `Optional` types

### 2. Recursive Type Inference Limitations

**Problem**: Codon cannot handle complex recursive tuple types, such as `Tuple[str, Tuple[...], float]`.

**Specific Issues**:
- Canonical signature methods with recursive tuple structures failed type inference
- Complex nested type annotations caused compilation errors

**Solution**: 
- Switched to string-based canonical signatures
- Avoided complex recursive type structures
- Used simpler, more predictable type patterns

### 3. Set Type Limitations

**Problem**: Codon lacks `frozenset` and has limited support for `set` with complex objects.

**Specific Issues**:
- `Set[TreeNode]` caused internal type checking errors
- No built-in support for order-independent comparisons

**Solution**:
```codon
@extend
class set:
    def __hash__(self):
        # Custom hash implementation for complex objects
```

### 4. Module Import System Differences

**Problem**: Codon's module system differs from Python, lacking support for `sys.path.append` and complex relative imports.

**Specific Issues**:
- Cannot import modules from different directories
- No support for dynamic module path manipulation

**Solution**:
- Placed all related files in the same directory
- Used simple, direct imports
- Avoided complex module hierarchies

### 5. Floating-Point Precision and Comparison

**Problem**: Floating-point comparison precision issues with `==` operator.

**Specific Issues**:
- Distance calculation results showed minor discrepancies
- Tree equality comparisons failed due to precision errors

**Solution**:
- Used `math.isclose()` for floating-point comparisons
- Implemented `round(distance, 12)` for stable comparisons
- Added tolerance-based equality checks

### 6. File Path and Data Structure Inconsistencies

**Problem**: Inconsistent file paths and data structure loading methods between Python and Codon versions.

**Specific Issues**:
- NumPy array loading with mismatched `dtype` parameters
- File path resolution differences

**Solution**:
- Unified use of `dtype=np.int64` for integer arrays
- Standardized file paths for test data
- Consistent data loading patterns

## Key Technical Solutions

### 1. Canonical Signature Method

Implemented a robust tree comparison system using string-based signatures:

```codon
def _canon_sig(self) -> str:
    dist = round(self.distance, 12)
    if self.is_leaf():
        idx = self.index if self.index is not None else -1
        return f"L({idx}:{dist})"
    child_sigs = [child._canon_sig() for child in self.children]
    child_sigs.sort()
    return f"N({';'.join(child_sigs)}:{dist})"
```

### 2. Set Extension Implementation

Extended Codon's `set` class to support complex object hashing:

```codon
@extend
class set:
    def __hash__(self):
        MAX = int.MAX
        MASK = 2 * MAX + 1
        n = len(self)
        h = 1927868237 * (n + 1)
        h &= MASK
        for x in self:
            hx = hash(x)
            h ^= (hx ^ (hx << 16) ^ 89869747) * 3644798167
            h &= MASK
        h = h * 69069 + 907133923
        h &= MASK
        if h > MAX:
            h -= MASK + 1
        if h == -1:
            h = 590923713
        return h
```

### 3. Type Unification Strategy

- Unified use of `np.float64` to avoid type conversion issues
- Explicit handling of `Optional` types to prevent `None` unpacking errors
- Consistent type annotations across all modules

## Performance Results

### Benchmark Results

| Run | Python (ms) | Codon (ms) | Speedup |
|-----|-------------|------------|---------|
| 1   | 7,456       | 1,522      | 4.9x    |
| 2   | 11,455      | 1,525      | 7.5x    |
| 3   | 10,716      | 1,092      | 9.8x    |
| 4   | 6,350       | 1,246      | 5.1x    |

**Average Speedup**: **6.8x**

### Performance Analysis

- **Consistent Improvement**: Codon consistently outperformed Python across all test runs
- **Stable Performance**: Codon execution times were more stable (1,092-1,525ms range)
- **Python Variability**: Python performance showed more variability (6,350-11,455ms range)

## Key Learnings and Insights

### 1. Importance of "Minimal Changes" Principle

- **Initial Approach**: Attempted significant rewrites, leading to numerous issues
- **Successful Approach**: Strict adherence to original Cython code with minimal modifications
- **Lesson**: Preserving algorithm logic while only changing syntax and type annotations is more effective

### 2. Understanding Codon's Type System

- **Design Philosophy**: Codon's type system prioritizes performance over flexibility
- **Best Practices**: 
  - Use strings and simple types over complex object types
  - Avoid recursive types and complex generics
  - Design types carefully from the beginning

## Project Structure

```
week3/
├── code/
│   ├── tree_minimal.codon      # Tree and TreeNode classes
│   ├── upgma_minimal.codon     # UPGMA algorithm
│   ├── nj_minimal.codon        # Neighbor Joining algorithm
│   └── test_phylo_minimal.codon # Test suite
├── test/
│   ├── test_phylo.py           # Python reference tests
│   └── tests/sequence/data/    # Test data files
├── evaluate.sh                 # Performance evaluation script

```


