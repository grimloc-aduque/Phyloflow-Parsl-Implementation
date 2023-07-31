

from appfuture_manager import AppFutureManager
from filesystem_util import ROOT, generate_subdir
from workflow_tasks import *

# --------------------- Function Calling ---------------------

def fcall_execute(run_function, inputs):
    future_id = AppFutureManager.new_future_id(run_function)
    future_dir = generate_subdir(AppFutureManager.DIR, future_id)
    future = run_function(inputs, future_dir)
    print(future)
    AppFutureManager.index(future_id, future)
    return future_id

def fcall_from_files(run_function, inputs:list[str]):
    inputs = format_files(ROOT, inputs)
    return fcall_execute(run_function, inputs)


# --------------------- VCF Transform ---------------------

def fcall_vcf_transform_from_files(vep_vcf:str):
    inputs = [vep_vcf]
    return fcall_from_files(run_vcf_transform, inputs)


# --------------------- Pyclone Vi Clustering ---------------------

def fcall_pyclone_vi_from_files(pyclone_vi_formatted:str):
    inputs = [pyclone_vi_formatted]
    return fcall_from_files(run_pyclone_vi, inputs)

def fcall_pyclone_vi_from_futures(vcf_future_id:str):
    vcf_future = AppFutureManager.query(vcf_future_id)
    inputs = get_inputs_pyclone_vi(vcf_future)
    return fcall_execute(run_pyclone_vi, inputs)


# --------------------- Cluster Transform ---------------------

def fcall_cluster_transform_from_files(pyclone_vi_formatted:str, cluster_assignment:str):
    inputs = [pyclone_vi_formatted, 
              cluster_assignment]
    return fcall_from_files(run_cluster_transform, inputs)

def fcall_cluster_transform_from_futures(vcf_future_id:str, pyclone_future_id:str):
    vcf_future = AppFutureManager.query(vcf_future_id)
    pyclone_future = AppFutureManager.query(pyclone_future_id)
    inputs = get_inputs_cluster_transform(vcf_future, pyclone_future)
    return fcall_execute(run_cluster_transform, inputs)


# --------------------- Spruce Tree ---------------------

def fcall_spruce_tree_from_files(spruce_formatted:str):
    inputs = [spruce_formatted]
    return fcall_from_files(run_spruce_tree, inputs)

def fcall_spruce_tree_from_futures(cluster_future_id:str):
    cluster_future = AppFutureManager.query(cluster_future_id)
    inputs = get_inputs_spruce_tree(cluster_future)
    return fcall_execute(run_spruce_tree, inputs)


# --------------------- Aggregate JSON ---------------------

def fcall_aggregate_json_from_files(vep_vcf:str, cluster_assignment:str,
                                    spruce_json:str, spruce_gz:str):
    inputs = [vep_vcf, 
              cluster_assignment, 
              spruce_json, 
              spruce_gz]
    return fcall_from_files(run_aggregate_json, inputs)

def fcall_aggregate_json_from_futures(vep_vcf:str, pyclone_future_id:AppFuture, 
                                      spruce_future_id:AppFuture):
    pyclone_future = AppFutureManager.query(pyclone_future_id)
    spruce_future = AppFutureManager.query(spruce_future_id)
    inputs = get_inputs_aggregate_json(vep_vcf, pyclone_future, spruce_future)
    return fcall_execute(run_aggregate_json, inputs)


# --------------------- Full Workflow ---------------------

def fcall_full_workflow(vep_vcf:str):    
    vcf_future_id = fcall_vcf_transform_from_files(
        vep_vcf=vep_vcf
    )
    pyclone_future_id = fcall_pyclone_vi_from_futures(
        vcf_future_id=vcf_future_id
    )
    cluster_future_id = fcall_cluster_transform_from_futures(
        vcf_future_id=vcf_future_id,
        pyclone_future_id=pyclone_future_id
    )
    spruce_future_id = fcall_spruce_tree_from_futures(
        cluster_future_id=cluster_future_id
    )
    aggregate_future_id = fcall_aggregate_json_from_futures(
        vep_vcf=vep_vcf,
        pyclone_future_id=pyclone_future_id,
        spruce_future_id=spruce_future_id
    )
    return aggregate_future_id


# --------------------- Parallel Workflows ---------------------

def fcall_parallel_workflows(vep_vcf_files:list[str]):
    future_ids = []
    for vep_vcf in vep_vcf_files:
        future_id = fcall_full_workflow(
            vep_vcf=vep_vcf
        )
        future_ids.append(future_id)

    futures = [AppFutureManager.query(id) for id in future_ids]
    inputs = get_inputs_aggregate_workflows(futures)
    return fcall_execute(run_aggregate_workflows, inputs)
