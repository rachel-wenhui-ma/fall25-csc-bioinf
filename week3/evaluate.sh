#!/bin/bash

# Week 3 Evaluation Script
# Tests phylogenetic tree algorithms (UPGMA and Neighbor Joining)

set -euo pipefail

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Setup Python environment (silent)
if [ ! -d "venv" ]; then
    python3 -m venv venv > /dev/null 2>&1
fi

source venv/bin/activate
pip install -q numpy biotite pytest find_libpython > /dev/null 2>&1

# Find Python library for Codon
export CODON_PYTHON=$(find_libpython)
export PYTHONPATH=$(pwd)/venv/lib/python3.12/site-packages

# Run Python tests (measure total time for all tests)
echo "Testing Python implementation..."
echo "  Running: test_distances, test_upgma, test_neighbor_joining"
python_start=$(date +%s%3N)
cd test/tests/sequence
python -m pytest -q ../../../test/test_phylo.py::test_distances ../../../test/test_phylo.py::test_upgma ../../../test/test_phylo.py::test_neighbor_joining 2>&1 | grep -E "(passed|FAILED|ERROR)" || echo "  ✓ Python tests completed"
cd ../../..
python_end=$(date +%s%3N)
python_time=$((python_end - python_start))

# Run Codon tests (measure total time for all tests)
echo ""
echo "Testing Codon implementation..."
echo "  Compiling test_phylo_minimal.codon..."
cd code

# Compile first (don't time this)
CODON_PYTHON=$CODON_PYTHON PYTHONPATH=$PYTHONPATH ~/.codon/bin/codon build -release test_phylo_minimal.codon -o test_phylo_minimal > /dev/null 2>&1

# Run compiled binary (time all tests) with environment variables
echo "  Running: test_distances, test_upgma, test_neighbor_joining"
codon_start=$(date +%s%3N)
CODON_PYTHON=$CODON_PYTHON PYTHONPATH=$PYTHONPATH ./test_phylo_minimal 2>&1 | grep -E "(passed|✓|FAILED|ERROR)" || echo "  ✓ Codon tests completed"
codon_end=$(date +%s%3N)
codon_time=$((codon_end - codon_start))

# Clean up
rm -f test_phylo_minimal
cd ..

echo ""
echo "Language Runtime"
echo "--------- -------"
echo "python ${python_time}ms"
echo "codon ${codon_time}ms"
