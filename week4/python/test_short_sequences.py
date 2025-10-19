#!/usr/bin/env python3
"""Test alignment algorithms on short sequences (q1-t1, q2-t2, etc.)."""

import os.path
from alignments import global_alignment, local_alignment, fitting_alignment, affine_global
from fasta_io import read_all_fasta


def run_short_sequence_tests():
    """
    Run four alignment algorithms on short test sequences.
    Test pairs: q1-t1, q2-t2, q3-t3, q4-t4, q5-t5
    """
    DATA_DIR = "../data"

    results = []

    # Read all sequences from q1.fa and t1.fa files
    q_file = os.path.join(DATA_DIR, "q1.fa")
    t_file = os.path.join(DATA_DIR, "t1.fa")
    
    q_sequences = read_all_fasta(q_file)
    t_sequences = read_all_fasta(t_file)
    
    # Pair up sequences by index (q1 with t1, q2 with t2, etc.)
    for (q_header, q_seq), (t_header, t_seq) in zip(q_sequences, t_sequences):
        print(f"\n=== Running {q_header} vs {t_header} ===")
        row = {"query": q_header, "target": t_header}

        # 1. Global alignment
        score, _, _ = global_alignment(q_seq, t_seq)
        row["Global_score"] = score

        # 2. Local alignment
        score, _, _ = local_alignment(q_seq, t_seq)
        row["Local_score"] = score

        # 3. Fitting alignment
        score, _, _ = fitting_alignment(q_seq, t_seq)
        row["Fitting_score"] = score

        # 4. Affine-gap global alignment
        score, _, _ = affine_global(q_seq, t_seq)
        row["Affine_score"] = score

        results.append(row)

    # Print results
    print("\n" + "="*80)
    print("SHORT SEQUENCE ALIGNMENT RESULTS")
    print("="*80)
    for row in results:
        print(f"\nQuery: {row['query']}, Target: {row['target']}")
        print(f"  Global score:  {row['Global_score']}")
        print(f"  Local score:   {row['Local_score']}")
        print(f"  Fitting score: {row['Fitting_score']}")
        print(f"  Affine score:  {row['Affine_score']}")
    print("\n" + "="*80)
    print("All short sequence alignments completed.")


if __name__ == "__main__":
    run_short_sequence_tests()


