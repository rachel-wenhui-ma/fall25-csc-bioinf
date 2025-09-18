# Week 1: Genome Assembly with Python and Codon

**Repository**: https://github.com/rachel-wenhui-ma/fall25-csc-bioinf

**BLAST Results**: 
# Data1: Porphyromonas gingivalis[CFB group bacteria]
# Data2: Porphyromonas gingivalis[CFB group bacteria]
# Data3: Paracidovorax citrulli AAC00-1[b-proteobacteria]
# Data4: Lacrimispora saccharolytica[firmicutes]

## Python Results
```
Dataset | Runtime | N50   | Contigs
--------|---------|-------|--------
data1   | 0:13    | 9990  | 20
data2   | 0:27    | 9992  | 20  
data3   | 0:34    | 9824  | 20
data4   | 5:53    | 159255| 20
```

## Codon Results
```
Dataset | Runtime | N50   | Contigs
--------|---------|-------|--------
data1   | 0:21    | 9991  | 20
data2   | 0:47    | 10014 | 20
data3   | 0:56    | 9825  | 20  
data4   | 12:03   | 173802| 20
```

**Problem**: Codon version (first attempt): running data4 caused a segmentation fault (core dumped) at runtime. So some changes have been made:

- Python version used recursive DFS with visited flag.

- Codon recursion caused type mismatches and instability, so we rewrote _get_depth using an explicit stack (iterative DFS).

- This removed stack overflow risks, but introduced differences in traversal order.

- In Codon, we adjusted _delete_path and node visited states to avoid dangling references.

- Introduced three-state visited system (0 = unvisited, 1 = visiting, 2 = visited) instead of Python’s simple boolean.

- This made Codon stable, but not identical in behavior.

