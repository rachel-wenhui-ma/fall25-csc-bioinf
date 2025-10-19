import os.path

from alignments import global_alignment, local_alignment, fitting_alignment, affine_global
from fasta_io import read_all_fasta


def run_all_tests():
    """
    Run four alignment algorithms:
        1. Global (Needleman–Wunsch)
        2. Local (Smith–Waterman)
        3. Fitting (semi-global)
        4. Global with affine gap penalty
    The following pairs are tested:
        q1-t1, q2-t2, q3-t3, q4-t4, q5-t5, MT-human vs MT-orang
    Results are saved in 'align_results.csv' at project root.
    """
    DATA_DIR = "../data"

    results = []

    # Read all sequences from q*.fa and t*.fa files
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
    
    # Also test MT-human vs MT-orang
    # mt_human = read_all_fasta(DATA_DIR / "MT-human.fa")
    # mt_orang = read_all_fasta(DATA_DIR / "MT-orang.fa")
    
    # if mt_human and mt_orang:
    #     q_header, q_seq = mt_human[0]
    #     t_header, t_seq = mt_orang[0]
        
    #     print(f"\n=== Running {q_header} vs {t_header} ===")
    #     row = {"query": q_header, "target": t_header}

    #     # 1. Global alignment
    #     score, _, _ = global_alignment(q_seq, t_seq)
    #     row["Global_score"] = score

    #     # 2. Local alignment
    #     score, _, _ = local_alignment(q_seq, t_seq)
    #     row["Local_score"] = score

    #     # 3. Fitting alignment
    #     score, _, _ = fitting_alignment(q_seq, t_seq)
    #     row["Fitting_score"] = score

    #     # 4. Affine-gap global alignment
    #     score, _, _ = affine_global(q_seq, t_seq)
    #     row["Affine_score"] = score

    #     results.append(row)

    # Print results
    print("\n" + "="*80)
    print("ALIGNMENT RESULTS")
    print("="*80)
    for row in results:
        print(f"\nQuery: {row['query']}, Target: {row['target']}")
        print(f"  Global score:  {row['Global_score']}")
        print(f"  Local score:   {row['Local_score']}")
        print(f"  Fitting score: {row['Fitting_score']}")
        print(f"  Affine score:  {row['Affine_score']}")
    print("\n" + "="*80)
    print("All alignments completed.")


if __name__ == "__main__":
    run_all_tests()
