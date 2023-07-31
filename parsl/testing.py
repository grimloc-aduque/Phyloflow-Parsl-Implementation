
import os

from filesystem_util import DATA_DIR
from function_calls import *
from workflow_tasks import *

# --------------------- Test Files ---------------------

test_files = {
    'vep_vcf': 'VEP_raw.A25.mutect2.filtered.snp.vcf',
    'pyclone_vi_formatted': 'pyclone_vi_formatted.tsv',
    'cluster_assignment': 'cluster_assignment.tsv',
    'spruce_formatted': 'spruce_formatted.tsv',
    'spruce_json': 'spruce.res.json',
    'spruce_gz': 'spruce.res.gz'    
}

for k,v in test_files.items():
    test_files[k] = os.path.join(DATA_DIR, v)


# --------------------- Unit Testing ---------------------


def test_vcf_transform():
    fcall_vcf_transform_from_files(
        vep_vcf=test_files['vep_vcf']
    )

def test_pyclone_vi():
    fcall_pyclone_vi_from_files(
        pyclone_vi_formatted=test_files['pyclone_vi_formatted']
    )

def test_cluster_transform():
    fcall_cluster_transform_from_files(
        pyclone_vi_formatted=test_files['pyclone_vi_formatted'],
        cluster_assignment=test_files['cluster_assignment']
    )

def test_spruce_tree():
    fcall_spruce_tree_from_files(
        spruce_formatted=test_files['spruce_formatted']
    )

def test_aggregate_json():
    fcall_aggregate_json_from_files(
        vep_vcf=test_files['vep_vcf'],
        cluster_assignment=test_files['cluster_assignment'],
        spruce_json=test_files['spruce_json'],
        spruce_gz=test_files['spruce_gz']
    )

def test_full_workflow():
    future_id = fcall_full_workflow(
        vep_vcf=test_files['vep_vcf']
    )
    AppFutureManager.query(future_id).result()

def test_parallel_workflows():
    future_id = fcall_parallel_workflows(
        vep_vcf_files=[test_files['vep_vcf']]*3
    )
    AppFutureManager.query(future_id).result()