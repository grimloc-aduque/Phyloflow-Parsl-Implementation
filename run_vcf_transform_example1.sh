#!/bin/bash

# eg.
#	> bash run_pyclone_example1.sh

# Run vcf_transform against the example data that it comes with. Will produce outputs for
# both pyclone and pyclone_vi to input.

FILE=./example_data/VEP_raw.A25.mutect2.filtered.snp.vcf
miniwdl run --dir=runs/ vcf_transform/vcf-transform-task.wdl vcf_type=mutect vcf_file=$FILE
