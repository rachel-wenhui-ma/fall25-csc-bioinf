#!/usr/bin/env python3

import os.path
from alignments import global_alignment, local_alignment, fitting_alignment, affine_global
from fasta_io import read_all_fasta
import time

def run_long_sequence_test():
    """Test alignment algorithms on long sequences (MT-human vs MT-orang)."""
    DATA_DIR = "../data"
    
    # Read MT sequences
    mt_human_file = os.path.join(DATA_DIR, "MT-human.fa")
    mt_orang_file = os.path.join(DATA_DIR, "MT-orang.fa")
    
    print("Loading sequences...")
    mt_human = read_all_fasta(mt_human_file)
    mt_orang = read_all_fasta(mt_orang_file)
    
    if not mt_human or not mt_orang:
        print("Error: Could not load MT sequences")
        return
    
    q_header, q_seq = mt_human[0]
    t_header, t_seq = mt_orang[0]
    
    print(f"\nSequence lengths:")
    print(f"  {q_header}: {len(q_seq)} bp")
    print(f"  {t_header}: {len(t_seq)} bp")
    print("\n" + "="*80)
    print(f"Running {q_header} vs {t_header}")
    print("="*80)
    
    # 1. Global alignment
    print("\n1. Global Alignment (Needleman-Wunsch)...")
    start = time.time()
    score, _, _ = global_alignment(q_seq, t_seq)
    elapsed = int((time.time() - start) * 1000)
    print(f"   Score: {score}")
    print(f"   Time: {elapsed}ms")
    
    # 2. Local alignment
    print("\n2. Local Alignment (Smith-Waterman)...")
    start = time.time()
    score, _, _ = local_alignment(q_seq, t_seq)
    elapsed = int((time.time() - start) * 1000)
    print(f"   Score: {score}")
    print(f"   Time: {elapsed}ms")
    
    # 3. Fitting alignment
    print("\n3. Fitting Alignment (Semi-global)...")
    start = time.time()
    score, _, _ = fitting_alignment(q_seq, t_seq)
    elapsed = int((time.time() - start) * 1000)
    print(f"   Score: {score}")
    print(f"   Time: {elapsed}ms")
    
    # 4. Affine-gap global alignment
    print("\n4. Affine Gap Global Alignment...")
    start = time.time()
    score, _, _ = affine_global(q_seq, t_seq)
    elapsed = int((time.time() - start) * 1000)
    print(f"   Score: {score}")
    print(f"   Time: {elapsed}ms")
    
    print("\n" + "="*80)
    print("Long sequence tests completed!")
    print("="*80)

if __name__ == "__main__":
    run_long_sequence_test()

