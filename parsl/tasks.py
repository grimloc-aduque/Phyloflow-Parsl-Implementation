
import json
import os
from typing import List

from filesystem_util import format_files, generate_task_dir, get_stdfiles

from parsl import bash_app, python_app
from parsl.data_provider.files import File
from parsl.dataflow.futures import AppFuture

# --------------------- VCF Transform ---------------------

@bash_app
def vcf_transform(samples_dir, inputs=[], outputs=[], 
                  stdout=None, stderr=None):
    return f''' 
        cd './vcf_transform/code';
        conda run -n vcf-transform python -B -m py_code.main mutect \\
        {inputs[0]} {outputs[0]} {outputs[1]} {outputs[2]} {samples_dir}
        '''

def run_vcf_transform(inputs:list, rundir:str) -> AppFuture:
    outdir = generate_task_dir(rundir)
    samples_dir = f'{outdir}/pyclone_samples'
    os.makedirs(samples_dir)
    outputs = [
        'headers.json',
        'mutations.json',
        'pyclone_vi_formatted.tsv'
    ]
    outputs = format_files(outdir, outputs)
    stdout, stderr = get_stdfiles(outdir)
    vcf_future = vcf_transform(inputs=inputs, outputs=outputs, 
                               stdout=stdout, stderr=stderr,
                               samples_dir=samples_dir,)
    return vcf_future



# --------------------- Pyclone Vi Clustering ---------------------

@bash_app
def pyclone_vi(inputs=[], outputs=[], 
               stdout=None, stderr=None):
    return f'''
        conda run -n pyclone-vi pyclone-vi fit --in-file {inputs[0]} --out-file {outputs[0]}
        conda run -n pyclone-vi pyclone-vi write-results-file --in-file {outputs[0]} --out-file {outputs[1]}
        '''

def get_inputs_pyclone_vi(vcf_future:AppFuture):
    inputs = [
        vcf_future.outputs[2]
    ]
    return inputs


def run_pyclone_vi(inputs:list, rundir:str) -> AppFuture:
    outdir = generate_task_dir(rundir)
    outputs = [
        'cluster_fit.hdf5',
        'cluster_assignment.tsv'
    ]
    outputs = format_files(outdir, outputs)
    stdout, stderr = get_stdfiles(outdir)
    pyclone_future = pyclone_vi(inputs=inputs, outputs=outputs,
                                stdout=stdout, stderr=stderr)
    return pyclone_future



# --------------------- Cluster Transform ---------------------

@bash_app
def cluster_transform(alpha, cluster_type, inputs=[], outputs=[], 
                      stdout=None, stderr=None):
    return f''' 
        cd './cluster_transform/code' ;
        conda run -n cluster-transform python -B -m \\
        py_code.main -t {cluster_type} -c {inputs[1]} -a {alpha} -o {outputs[0]} -v {inputs[0]}
        '''

def get_inputs_cluster_transform(vcf_future:AppFuture, 
                                 pyclone_future:AppFuture):
    inputs = [
        vcf_future.outputs[2],
        pyclone_future.outputs[1]
    ]
    return inputs

def run_cluster_transform(inputs:list, rundir:str):
    outdir = generate_task_dir(rundir)
    outputs = [
        'spruce_formatted.tsv'
    ]
    outputs = format_files(outdir, outputs)
    stdout, stderr = get_stdfiles(outdir)
    cluster_future = cluster_transform(alpha=0.05, cluster_type='pyclone-vi',
                                       inputs=inputs, outputs=outputs,
                                       stdout=stdout, stderr=stderr)
    return cluster_future



# --------------------- Spruce Tree ---------------------

@bash_app
def spruce_tree(inputs=[], outputs=[], 
                stdout=None, stderr=None):
    return f''' 
        ./spruce/tool/cliques -s -1 {inputs[0]} > {outputs[0]}
        ./spruce/tool/enumerate -clique {outputs[0]} -t 2 -v 3 {inputs[0]} > {outputs[1]}
        gzip -c {outputs[1]} > {outputs[2]}
        zcat {outputs[2]} | ./spruce/tool/rank - > {outputs[3]}
        zcat {outputs[2]} | ./spruce/tool/visualize -i 0 -a - > {outputs[4]}
        zcat {outputs[2]} | ./spruce/tool/visualize -i 0 -j - > {outputs[5]}
        '''

def get_inputs_spruce_tree(cluster_future:AppFuture):
    inputs = [
        cluster_future.outputs[0]
    ]
    return inputs

def run_spruce_tree(inputs:list, rundir:str) -> AppFuture:
    outdir = generate_task_dir(rundir)
    outputs = [
        'spruce.cliques', 
        'spruce.res',
        'spruce.res.gz',
        'spruce.merged.res',
        'spruce.res.txt',
        'spruce.res.json'
    ]
    outputs = format_files(outdir, outputs)
    stdout, stderr = get_stdfiles(outdir)
    spruce_future = spruce_tree(inputs=inputs, outputs=outputs,
                                stdout=stdout, stderr=stderr)
    return spruce_future
    


# --------------------- Aggregate JSON ---------------------

@bash_app
def aggregate_json(vcf_type, inputs=[], outputs=[], 
                   stdout=None, stderr=None):
    return f''' 
        cd './aggregate_json/code' ;
		conda run -n aggregate-json python aggregate_json.py \\
			-v {inputs[0]} \\
			-c {inputs[1]} \\
			-s {inputs[2]} \\
			-S {inputs[3]} \\
			-j {outputs[0]} \\
			--program {vcf_type}
        '''

def get_inputs_aggregate_json(input_file:File, 
                              pyclone_future:AppFuture, 
                              spruce_future:AppFuture):
    inputs = [
        input_file,
        pyclone_future.outputs[1],
        spruce_future.outputs[5],
        spruce_future.outputs[2]
    ]
    return inputs

def run_aggregate_json(inputs:list, rundir:str) -> AppFuture:
    outdir = generate_task_dir(rundir)
    outputs = [
        'aggregated.json'
    ]
    outputs = format_files(outdir, outputs)
    stdout, stderr = get_stdfiles(outdir)
    aggregate_future = aggregate_json(vcf_type = 'mutect',
                                      inputs=inputs, outputs=outputs,
                                      stdout=stdout, stderr=stderr )
    return aggregate_future



# --------------------- Aggregate Workflows ---------------------

@python_app
def aggregate_workflows(inputs=[], outputs=[]):
    output_json = []
    for file in inputs:
        workflow_json = json.load(open(file))
        output_json.append(workflow_json)
    output_file = open(outputs[0], 'w')
    output_file.write(json.dumps(output_json))
    output_file.close()


def run_aggregate_workflows(aggregate_json_futures:List[AppFuture], rundir):
    inputs = [f.outputs[0] for f in aggregate_json_futures]
    outputs = [
        'aggregated_workflows.json'
    ]
    outputs = format_files(rundir, outputs)
    aggregate_workflows_future = aggregate_workflows(inputs=inputs, outputs=outputs)
    return aggregate_workflows_future
