#!/bin/bash

# eg.
#   > bash run_aggregate_json.sh

VEP_FILE=./example_data/VEP_raw.A25.mutect2.filtered.snp.vcf
CLUSTER_ASSIGNMENT=./example_data/cluster_assignment.tsv
SPRUCE_JSON=./example_data/spruce.res.json
SPRUCE_RES=./example_data/spruce.res.gz
VCF_TYPE=mutect

# 1. `VEP_FILE`: the VEP output annotation of a somatic VCP variant file.
#    - e.g. `example_data/mek_lab_vcfs/VEP_raw.A25.mutect2.filtered.snp.vcf`
# 2. `CLUSTER_ASSIGNMENT`: the PyClone-VI assignment of sample variants to specific mutation clusters.
#    - e.g. `example_data/cluster/pyclone_vi_cluster_assignment.tsv`
# 3. `SPRUCE_JSON`: SPRUCE description of the structure of the inferred trees.
#    - e.g. `example_data/spruce/spruce.res.json`
# 4. `SPRUCE_RES`: SPRUCE description of the different tree inference solutions with subclone proportions.
#    - e.g. `example_data/spruce/spruce.res.gz`

miniwdl run --dir=runs/ aggregate_json/aggregate-json-task.wdl \
    vep_file=$VEP_FILE \
    cluster_assignment=$CLUSTER_ASSIGNMENT \
    spruce_json=$SPRUCE_JSON \
    spruce_res=$SPRUCE_RES \
    vcf_type=$VCF_TYPE
