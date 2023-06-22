
import copy
import os
from time import time

from filesystem_util import (DATA_DIR, RUNS_DIR, TEST_DIR, format_files,
                             generate_run_dir)
from tasks import *
from workflow import run_parallel_workflows, run_workflow

from parsl.data_provider.files import File

# --------------------- Unit Testing ---------------------

def test_task(inputs, run_task_func):
    inputs = format_files(DATA_DIR, inputs)
    future = run_task_func(inputs, TEST_DIR)
    print(future)
    future.result()

def test_vcf_transform():
    inputs = ['VEP_raw.A25.mutect2.filtered.snp.vcf']
    test_task(inputs, run_vcf_transform)

def test_pyclone_vi():
    inputs = ['pyclone_vi_formatted.tsv']
    test_task(inputs, run_pyclone_vi)

def test_cluster_transform():
    inputs = ['pyclone_vi_formatted.tsv', 
              'cluster_assignment.tsv']
    test_task(inputs, run_cluster_transform)

def test_spruce_tree():
    inputs = ['spruce_formatted.tsv']
    test_task(inputs, run_spruce_tree)

def test_aggregate_json():
    inputs = ['VEP_raw.A25.mutect2.filtered.snp.vcf',
              'cluster_assignment.tsv',
              'spruce.res.json',
              'spruce.res.gz']
    test_task(inputs, run_aggregate_json)



# --------------------- Integration Testing ---------------------

def test_workflow():
    rundir = generate_run_dir(RUNS_DIR)
    inputs = [File('VEP_raw.A25.mutect2.filtered.snp.vcf')]
    inputs = format_files(DATA_DIR, inputs)
    future = run_workflow(inputs[0], rundir)
    print(future)
    future.result()


def test_parallel_workflows():
    rundir = generate_run_dir(RUNS_DIR)
    input_file = os.path.join(DATA_DIR, 'VEP_raw.A25.mutect2.filtered.snp.vcf')
    input_file = File(input_file)
    files = []
    for _ in range(3):
        files.append(copy.deepcopy(input_file))

    start = time()
    last_future = run_parallel_workflows(files, rundir)
    last_future.result()
    end = time()
    print("\nAll Workflows Finished !")
    print(f"Elapsed Time: {round(end - start, 2)} [seconds]\n")