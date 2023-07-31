

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


# --------------------- Filesystem Management ---------------------

def generate_datetime_subdir(root_dir:str):
    date_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    run_dir = os.path.join(root_dir, date_time)
    os.mkdir(run_dir)
    return run_dir

def generate_subdir(root_dir:str, sub_dir:str):
    path = os.path.join(root_dir, sub_dir)
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)
    return path

def get_stdfiles(outdir:str):
    stdout = f'{outdir}/stdout.txt'
    stderr = f'{outdir}/stderr.txt'
    return stdout, stderr

def format_files(dir:str, files:List[str]):
    files = [os.path.join(dir, file) for file in files]
    files = [File(f) for f in files]
    return files