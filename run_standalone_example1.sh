#!/bin/bash

# eg.
#	> bash run_standalone_example1.sh

# Run standalone against the example data that it comes with. Will produce JSON combined output

VCFFILE=./example_data/A25.mutect2.filtered.snp.vcf
ANNOFILE=./example_data/VEP_raw.A25.mutect2.filtered.snp.vcf
miniwdl run --dir=runs/ workflows/phyloflow_standalone.wdl vcf_type=mutect vcf_input_file=$VCFFILE vep_input_file=$ANNOFILE
