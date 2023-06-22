#!/bin/bash

# eg.
#	> bash run_pyclone_example1.sh

# Run cluster_transform against the example data that it comes with. Will produce outputs for
# both pyclone and pyclone_vi to input.

PYCLONE_VI_CLUSTER=./example_data/cluster_assignment.tsv
ALPHA=0.05
PYCLONE_VI_INPUT=./example_data/pyclone_vi_formatted.tsv

miniwdl run --dir=runs/ cluster_transform/cluster-transform-task.wdl \
    cluster_type=pyclone-vi \
    cluster_tsv_file=$PYCLONE_VI_CLUSTER \
    alpha=$ALPHA \
    pyclone_vi_formatted=$PYCLONE_VI_INPUT
