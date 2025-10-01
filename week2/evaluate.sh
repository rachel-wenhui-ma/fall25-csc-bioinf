#!/bin/bash

set -euo pipefail

echo "=== Week 2: Bio.motifs Tests (Python baseline + Codon) ==="

PY=python3

# Ensure pip exists; try ensurepip if missing
if ! $PY -m pip --version >/dev/null 2>&1; then
  echo "pip not found; bootstrapping with ensurepip..."
  $PY -m ensurepip --upgrade >/dev/null 2>&1 || true
fi

# If pip exists now, install deps and run Python baselines
PY_OK=0
if $PY -m pip --version >/dev/null 2>&1; then
  echo "Installing Python deps (biopython, numpy)..."
  if $PY -m pip install --upgrade pip setuptools wheel && $PY -m pip install biopython numpy; then
    PY_OK=1
  else
    echo "pip install failed; skipping Python baselines"
  fi
else
  echo "Skipping Python baselines (pip unavailable)"
fi

if [ "$PY_OK" = "1" ]; then
  echo "-- Python: baseline BioPython tests"
  $PY test/baseline_biopython_tests.py -q || echo "baseline_biopython_tests failed"
  echo "-- Python: baseline codon2(py) tests"
  $PY test/baseline_codon2_py_tests.py -q || echo "baseline_codon2_py_tests failed"
fi

echo "-- Codon: codon2_* tests"
( cd code && ~/.codon/bin/codon run ../test/codon2_tests.py )

echo "=== Week 2: All tests completed ==="


