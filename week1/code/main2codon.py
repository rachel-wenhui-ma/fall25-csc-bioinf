from dbg2codon import DBG
from utils2codon import read_data
import sys

def main(argv: list[str]) -> None:
    input_path: str = "./" + argv[1] if not argv[1].startswith("./") else argv[1]

    short1, short2, long1 = read_data(input_path)

    k: int = 25
    dbg = DBG(k=k, data_list=[short1, short2, long1])

    # ✅ Changed output filename to contig2codon.fasta
    output_file: str = (input_path + "/contig2codon.fasta"
                        if not input_path.endswith("/")
                        else input_path + "contig2codon.fasta")

    with open(output_file, "w") as f:
        for i in range(20):
            c: str = dbg.get_longest_contig()
            if not c:   # empty string means no contig
                break
            print(i, len(c))
            f.write(f">contig_{i}\n")
            f.write(c + "\n")

if __name__ == "__main__":
    main(sys.argv)
