

from filesystem_util import LOGS_DIR
from testing import *

import parsl
from parsl.config import Config
from parsl.executors import ThreadPoolExecutor

# --------------------- Main Code ---------------------

def load_config():
    config = Config(
        executors=[
            ThreadPoolExecutor(
                label='threads',
                max_threads=4
            )
        ],
        run_dir=LOGS_DIR
    )
    parsl.load(config)


if __name__ == '__main__':

    load_config()

    # Unit Tests for every Task

    test_vcf_transform()
    test_pyclone_vi()
    test_cluster_transform()
    test_spruce_tree()
    test_aggregate_json()

    # Full Parallel Workflow

    test_workflow()
    test_parallel_workflows()


