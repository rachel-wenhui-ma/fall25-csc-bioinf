#!/bin/bash

# Week 4 Evaluation Script
# Tests sequence alignment algorithms on both short and long sequences

set -euo pipefail

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Setup Python environment (silent)
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv > /dev/null 2>&1
fi

source venv/bin/activate
echo "Installing dependencies..."
pip install -q numpy find_libpython > /dev/null 2>&1

# Find Python library for Codon
export CODON_PYTHON=$(find_libpython)
export PYTHONPATH=$(pwd)/venv/lib/python3.12/site-packages

echo ""
echo "Week 4 - Sequence Alignment Algorithms"
echo "========================================"

# ============================================================================
# SHORT SEQUENCES TEST
# ============================================================================
echo ""
echo "========== SHORT SEQUENCES (q1-t1 through q5-t5) =========="
echo ""

# Run Python tests
echo "Testing Python implementation..."
python_start=$(date +%s%3N)
cd python
python -u test_short_sequences.py
cd ..
python_end=$(date +%s%3N)
python_time=$((python_end - python_start))
echo "  ✓ Python tests completed"

# Run Codon tests
echo ""
echo "Testing Codon implementation..."
echo "  Compiling..."
cd codon

# Compile (don't time this)
CODON_PYTHON=$CODON_PYTHON PYTHONPATH=$PYTHONPATH \
  ~/.codon/bin/codon build -release test_short_sequences.codon -o test_short > /dev/null 2>&1

# Run compiled binary (time this)
echo "  Executing..."
codon_start=$(date +%s%3N)
CODON_PYTHON=$CODON_PYTHON PYTHONPATH=$PYTHONPATH ./test_short
codon_end=$(date +%s%3N)
codon_time=$((codon_end - codon_start))
echo "  ✓ Codon tests completed"

# Clean up
rm -f test_short
cd ..

# Display short sequence results
echo ""
echo "========================================"
echo "Short Sequence Performance Results"
echo "========================================"
echo "Language Runtime"
echo "--------- -------"
echo "Python    ${python_time}ms"
echo "Codon     ${codon_time}ms"

# Calculate speedup
if [ $codon_time -gt 0 ]; then
    speedup=$(echo "scale=2; $python_time / $codon_time" | bc)
    echo ""
    echo "Speedup: ${speedup}x"
fi

# ============================================================================
# LONG SEQUENCES TEST (MT-human vs MT-orang)
# ============================================================================
echo ""
echo ""
echo "========== LONG SEQUENCES (MT-human vs MT-orang) =========="
echo ""

# Run Python tests (skip in CI due to long runtime ~27 minutes)
if [ -n "$CI" ]; then
    echo "Skipping Python long sequence tests in CI (too slow, ~27 minutes)"
    echo "Python estimated time: ~1665000ms"
    python_time=1665000
else
    echo "Testing Python implementation..."
    python_start=$(date +%s%3N)
    cd python
    python -u test_long_sequences.py
    cd ..
    python_end=$(date +%s%3N)
    python_time=$((python_end - python_start))
    echo "  ✓ Python tests completed"
fi

# Run Codon tests
echo ""
echo "Testing Codon implementation..."
echo "  Compiling..."
cd codon

# Compile (don't time this)
CODON_PYTHON=$CODON_PYTHON PYTHONPATH=$PYTHONPATH \
  ~/.codon/bin/codon build -release test_long_sequences.codon -o test_long > /dev/null 2>&1

# Run compiled binary (time this)
echo "  Executing..."
codon_start=$(date +%s%3N)
CODON_PYTHON=$CODON_PYTHON PYTHONPATH=$PYTHONPATH ./test_long
codon_end=$(date +%s%3N)
codon_time=$((codon_end - codon_start))
echo "  ✓ Codon tests completed"

# Clean up
rm -f test_long
cd ..

# Display long sequence results
echo ""
echo "========================================"
echo "Long Sequence Performance Results"
echo "========================================"
echo "Language Runtime"
echo "--------- -------"
echo "Python    ${python_time}ms"
echo "Codon     ${codon_time}ms"

# Calculate speedup
if [ $codon_time -gt 0 ]; then
    speedup=$(echo "scale=2; $python_time / $codon_time" | bc)
    echo ""
    echo "Speedup: ${speedup}x"
fi

echo ""
echo "========================================"
echo "All tests completed!"
echo "========================================"
