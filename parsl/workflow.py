import shutil
from time import sleep
from typing import List

from filesystem_util import generate_workflow_dir
from tasks import *

from parsl.data_provider.files import File

# --------------------- Full Workflow ---------------------

def run_workflow(input_file:File, rundir:str) -> AppFuture:
    print(f"\nScheduling Workflow")
    print(f"Input file: {input_file}")
    print(f"Output dir: {rundir}")

    shutil.copy(input_file, rundir)
    inputs = [input_file]
    vcf_future = run_vcf_transform(inputs, rundir)

    inputs = get_inputs_pyclone_vi(vcf_future)
    pyclone_future = run_pyclone_vi(inputs, rundir)

    inputs = get_inputs_cluster_transform(vcf_future, pyclone_future)
    cluster_future = run_cluster_transform(inputs, rundir)

    inputs = get_inputs_spruce_tree(cluster_future)
    spruce_future = run_spruce_tree(inputs, rundir)

    inputs = get_inputs_aggregate_json(input_file, pyclone_future, spruce_future)
    aggregate_json_future = run_aggregate_json(inputs, rundir)
    
    futures = [vcf_future, pyclone_future, cluster_future, 
               spruce_future, aggregate_json_future]
    [print(f) for f in futures]
    return aggregate_json_future



# --------------------- Parallel Workflows ---------------------

def run_parallel_workflows(files:List[File], rundir:str) -> AppFuture:
    futures = []
    for idx, input_file in enumerate(files):
        workflow_dir = generate_workflow_dir(rundir, idx)
        workflow_future = run_workflow(input_file, workflow_dir)
        futures.append(workflow_future)
        sleep(0.5)

    print("\nScheduling Workflow Aggregation")
    last_future = run_aggregate_workflows(futures, rundir)
    print(last_future)
    return last_future