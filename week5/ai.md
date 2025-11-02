# AI Usage Log - Week 5

## Date: 2025-10-31 to 2025-11-02

### Tools Used
- Cursor AI Assistant (Claude Sonnet 4.5)
- GitHub Copilot (for code completion)

---

## Tasks Accomplished

### 1. **Initial Setup and Understanding (2025-10-31)**
- Understanding assignment requirements
- Learning minimap2 usage for alignment
- Setting up initial notebook structure
- Configuring GitHub Actions CI/CD pipeline
- Understanding reference genome download from UCSC

### 2. **Step 1-3: Data Download, Alignment, and Variant Calling**
- Implemented data download (Illumina and PacBio FASTQ files)
- Configured minimap2 with appropriate parameters (`-ax sr` for Illumina, `-ax map-pb` for PacBio)
- Set up bcftools for variant calling
- Handled file compression (bz2) and Unix pipes

### 3. **Step 4: Phasing with HapCUT2**
- Integrated HapCUT2 into pipeline
- Configured extractHAIRS for both Illumina and PacBio
- Generated phased VCF files with proper indexing
- Debugged phasing output and file naming issues

### 4. **Step 5: Variant Comparison Analysis**
- Implemented per-gene variant analysis for CYP2C19, CYP2C9, and CYP2C8
- Used `bcftools isec` to find shared and unique variants
- Parsed `sites.txt` to count variants by category (shared/Illumina-only/PacBio-only)
- Fixed chromosome naming issues (`chr10` vs `10`)
- Calculated concordance percentages for each gene

### 5. **Step 5.5: Automated IGV Screenshots**
- Created IGV batch script for automated screenshot generation
- Configured three specific variant positions:
  - chr10:94772788 (Illumina-only)
  - chr10:94947469 (PacBio-only)
  - chr10:94761900 (shared)
- Integrated IGV into CI/CD using `xvfb-run` for headless execution
- Fixed BAM/BAI loading issues (absolute paths, index file generation)
- Optimized IGV visualization parameters:
  - Window range (200bp with `-100bp/+100bp` context)
  - Display preferences (`SAM.SHOW_MISMATCHES`, `expand` mode)
  - Panel height (800px)
- Configured artifact upload in GitHub Actions

### 6. **Step 6: Star-Allele Identification**
- Researched PharmVar database and star-allele nomenclature
- Identified key marker variants for:
  - **CYP2C19**: *2 (rs4244285), *3 (rs4986893), *17 (rs12248560)
  - **CYP2C9**: *2 (rs1799853), *3 (rs1057910)
  - **CYP2C8**: *2 (rs11572080), *3 (rs10509681 + rs11572103)
- Implemented `bcftools query` commands to check marker variants
- Fixed FORMAT field syntax (`GT=[%GT]` instead of `GT=%GT`)
- Manually validated results by running queries locally
- Documented complete pharmacogenomic profile with clinical interpretations

---

## Key Problems Solved

### Problem 1: bcftools isec not producing expected output
**Issue**: Initial `bcftools isec` command was not generating separate VCFs for shared/unique variants correctly.

**Solution**: Changed approach to parse `sites.txt` output using awk to count variants by presence pattern (`11`=shared, `10`=Illumina-only, `01`=PacBio-only).

### Problem 2: PowerShell parsing errors with bash commands
**Issue**: Windows PowerShell couldn't handle complex bash commands with `&&` operators.

**Solution**: Wrapped bash commands in separate `.sh` script files or used `%%bash` magic in Jupyter cells.

### Problem 3: IGV screenshots empty or incorrect
**Issues**:
- Screenshots showed only reference track, no BAM reads
- BAM files not loading due to incorrect paths
- Missing BAI index files

**Solutions**:
- Fixed BAM file paths to use absolute paths
- Explicitly created BAI index files using `samtools index`
- Adjusted IGV batch script preferences for proper visualization
- Used `expand` mode and `SAM.SHOW_MISMATCHES` for base-level view

### Problem 4: IGV NoClassDefFoundError in CI
**Issue**: Manual IGV jar download in CI resulted in Java classpath errors.

**Solution**: Switched to `conda install -c bioconda igv` which properly handles all dependencies.

### Problem 5: bcftools query FORMAT field syntax error
**Issue**: `GT=%GT` caused error: "no such tag defined in the VCF header: INFO/GT"

**Solution**: Changed to `GT=[%GT]` because GT is a FORMAT field (per-sample), not INFO field, and must be enclosed in square brackets.

---

## Key Learning Points

### Bioinformatics Concepts
- **Variant Calling**: Using bcftools mpileup + call workflow
- **Phasing**: Understanding haplotype reconstruction with HapCUT2
- **VCF Format**: Difference between INFO and FORMAT fields
- **BAM/BAI**: Importance of index files for genomic viewers
- **Star-Alleles**: Pharmacogenomic nomenclature and clinical significance
- **Concordance Analysis**: Comparing results from different sequencing technologies

### Technical Skills
- Bash scripting in Jupyter notebooks
- GitHub Actions CI/CD configuration
- Headless GUI execution with xvfb
- IGV batch scripting for automation
- bcftools advanced queries and filtering
- Conda package management

### Debugging Strategies
- Verifying file existence and paths with `ls -lh`
- Checking file contents with `head`, `wc -l`, `bcftools view -H`
- Using `2>/dev/null` and `|| echo` for error handling
- Testing commands locally before adding to CI
- Reading tool documentation for correct syntax

---

## Prompts and Key Discussions

### Step-by-Step Questions
1. "都是0" → Debugging why variant counts were zero
2. "到底带不带chr" → Chromosome naming convention (`chr10` vs `10`)
3. "Do this analysis for every gene" → Understanding per-gene analysis requirement
4. "可以添加自动生成截图的代码了" → Implementing IGV automation
5. "xvfb 是干嘛的" → Understanding headless X server for GUI apps
6. "截图是不完整的，截图范围不对" → Iterative refinement of IGV parameters
7. "为什么这个图可以清晰看到变异的字母具体是什么" → Understanding IGV display modes
8. "step 6 要求我把所有的变异都查一遍吗" → Clarifying star-allele analysis scope

### Technical Investigations
- Difference between `0/1` (unphased) and `0|1` (phased) genotypes
- PharmVar database structure and star-allele definitions
- IGV batch script syntax and preferences
- bcftools query format string syntax
- Homopolymer regions and sequencing technology biases

---

## Time Investment

### Breakdown
- **Initial setup and Steps 1-3**: ~3 hours
- **Step 4 (Phasing)**: ~2 hours
- **Step 5 (Variant comparison)**: ~2 hours
- **Step 5.5 (IGV automation)**: ~4 hours (iterative debugging)
- **Step 6 (Star-alleles)**: ~2 hours (research + implementation + validation)
- **Documentation and refinement**: ~1 hour

**Total AI-assisted time**: ~14 hours

### What AI Helped With
✅ **Very Helpful:**
- Understanding tool syntax and parameters
- Debugging file format issues
- Writing bash scripts and CI/CD configurations
- Explaining biological concepts (star-alleles, phasing)
- Iterative refinement based on test results

⚠️ **Moderate Help:**
- Initial approach selection (sometimes required course correction)
- PharmVar database navigation (still required manual verification)

❌ **AI Couldn't Help:**
- Running actual commands locally (user had to test)
- Accessing PharmVar website directly
- Viewing actual screenshot outputs (user had to describe)

---

## Files Created/Modified

### Created
- `week5/week5.ipynb` - Main assignment notebook
- `week5/igv_batch_script.txt` - Automated IGV screenshot script
- Various temporary scripts (`run_step5_pergene.sh`, etc.) - later deleted

### Modified
- `.github/workflows/actions.yml` - Added Week 5 CI steps
- `week5/ai.md` - This file

### Generated Data (in CI)
- `results/illumina.bam`, `results/pacbio.bam` - Aligned reads
- `results/illumina_phased.vcf.gz`, `results/pacbio_phased.vcf.gz` - Phased variants
- `results/vcf_compare/sites.txt` - Variant comparison results
- `igv_images/auto/*.png` - Automated screenshots

---

## Reflection

### What Went Well
- Systematic approach to each step of the pipeline
- Good integration of automated testing via GitHub Actions
- Clear documentation in notebook with explanations
- Successful troubleshooting of complex technical issues

### What Was Challenging
- IGV automation took longer than expected due to multiple issues (paths, indexing, display settings)
- Understanding the difference between comprehensive star-allele calling vs. marker-based approach
- Balancing automation vs. manual interpretation for biological conclusions

### Key Takeaway
AI is excellent for:
1. **Learning new tools quickly** (minimap2, bcftools, HapCUT2, IGV batch mode)
2. **Debugging technical issues** (syntax errors, file paths, CI configuration)
3. **Understanding complex formats** (VCF structure, BAM requirements)
4. **Writing boilerplate code** (bash scripts, CI workflows)

But still requires:
1. **User testing and validation** - Can't blindly trust AI suggestions
2. **Domain knowledge** - Understanding what makes biological sense
3. **Iterative refinement** - Especially for visualization and presentation

---

## Honesty Statement

This assignment was completed with significant AI assistance from Cursor AI (Claude Sonnet 4.5) for:
- Code generation (bash scripts, bcftools commands, IGV batch scripts)
- Debugging and troubleshooting
- Understanding bioinformatics concepts
- Writing documentation and explanations

All code was tested and validated by the student. Biological interpretations were reviewed against peer-reviewed sources (PharmVar, CPIC guidelines). The student takes full responsibility for the correctness and integrity of this work.
