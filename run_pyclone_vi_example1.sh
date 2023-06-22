#!/bin/bash

# Run pyclone-vi against the synthetic data that it comes with.  There is no
# translation step as the inputs are already prepared by the pyclone-vi
# authors.  This runs the wdl 'task' directly, not part of an encapsulating
# 'workflow'

FILE=./example_data/pyclone_vi_formatted.tsv
miniwdl run --dir=runs/ pyclone_vi/pyclone-vi-task.wdl mutations_tsv=$FILE

