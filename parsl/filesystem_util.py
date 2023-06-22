

import inspect
import os
import shutil
from datetime import datetime
from typing import List

from parsl.data_provider.files import File

ROOT = os.getcwd()
DATA_DIR = os.path.join(ROOT, 'example_data')
PARSL_DIR = os.path.join(ROOT, 'parsl')

LOGS_DIR = os.path.join(PARSL_DIR, 'logs')
RUNS_DIR = os.path.join(PARSL_DIR, 'runs')
TEST_DIR = os.path.join(PARSL_DIR, 'tests')


# --------------------- Filesystem Management ---------------------

def generate_run_dir(root_dir:str):
    date_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    run_dir = os.path.join(root_dir, date_time)
    os.mkdir(run_dir)
    return run_dir

def generate_workflow_dir(root_dir:str, idx:int):
    workflow_dir = os.path.join(root_dir, f'run_workflow_{idx}')
    os.makedirs(workflow_dir)
    return workflow_dir

def generate_task_dir(root_dir:str):
    task_name = inspect.stack()[1][3]
    task_dir = os.path.join(root_dir, task_name)
    if os.path.exists(task_dir):
        shutil.rmtree(task_dir)
    os.makedirs(task_dir)
    return task_dir

def get_stdfiles(outdir:str):
    stdout = f'{outdir}/stdout.txt'
    stderr = f'{outdir}/stderr.txt'
    return stdout, stderr

def format_files(dir:str, files:List[str]):
    files = [os.path.join(dir, file) for file in files]
    files = [File(f) for f in files]
    return files