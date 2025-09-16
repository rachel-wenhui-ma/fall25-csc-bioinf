#!/bin/bash

# Set script to continue on error for debugging  
set -uo pipefail

# Function to calculate N50
calculate_n50() {
    local fasta_file="$1"
    
    # Extract contig lengths and sort in descending order
    lengths=$(grep -v '^>' "$fasta_file" | awk '{print length}' | sort -nr)
    
    # Calculate total length
    total_length=$(echo "$lengths" | awk '{sum += $1} END {print sum}')
    half_total=$((total_length / 2))
    
    # Find N50
    cumulative=0
    n50=0
    while IFS= read -r length; do
        cumulative=$((cumulative + length))
        if [ $cumulative -ge $half_total ]; then
            n50=$length
            break
        fi
    done <<< "$lengths"
    
    echo $n50
}

# Function to run experiment and calculate metrics
run_experiment() {
    local dataset="$1"
    local language="$2"
    local data_path="data/$dataset"
    
    # Record start time
    start_time=$(date +%s.%N)
    
    if [ "$language" = "python" ]; then
        cd code
        python3 main.py "../data/$dataset" >/dev/null 2>&1
        result=$?
        cd ..
        contig_file="$data_path/contig.fasta"
        if [ $result -ne 0 ]; then
            echo "$dataset,python,FAILED,N/A"
            return 0
        fi
    else
        cd code
        ~/.codon/bin/codon run -plugin seq main2codon.py "../data/$dataset" >/dev/null 2>&1
        result=$?
        cd ..
        contig_file="$data_path/contig2codon.fasta"
        if [ $result -ne 0 ]; then
            echo "$dataset,codon,FAILED,N/A"
            return 0
        fi
    fi
    
    # Record end time
    end_time=$(date +%s.%N)
    
    # Calculate runtime
    runtime=$(echo "$end_time - $start_time" | bc)
    
    # Ensure minimum runtime of 1 second for display
    runtime_int=$(echo "$runtime" | awk '{printf "%.0f", ($1 < 1 ? 1 : $1)}')
    
    # Format runtime as MM:SS
    minutes=$((runtime_int / 60))
    seconds=$((runtime_int % 60))
    formatted_time=$(printf "%d:%02d" $minutes $seconds)
    
    # Calculate N50
    if [ -f "$contig_file" ]; then
        n50=$(calculate_n50 "$contig_file")
    else
        n50="N/A"
        formatted_time="FAILED"
    fi
    
    echo "$dataset,$language,$formatted_time,$n50"
}

# Main execution
echo "Dataset,Language,Runtime,N50"

# Run experiments for all datasets
datasets=("data1" "data2" "data3" "data4")

for dataset in "${datasets[@]}"; do
    # Check if dataset exists
    if [ -d "data/$dataset" ]; then
        # Run Python version
        run_experiment "$dataset" "python"
        
        # Run Codon version
        run_experiment "$dataset" "codon"
    else
        echo "$dataset,python,N/A,N/A"
        echo "$dataset,codon,N/A,N/A"
    fi
done

