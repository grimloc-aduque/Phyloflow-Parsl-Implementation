

from filesystem_util import LOGS_DIR
from function_descriptions import functions
from openai_agent import OpenAIAgent
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

    print("\nIndividual Tasks\n")
    AppFutureManager.new_dir()
    test_vcf_transform()
    test_pyclone_vi()
    test_cluster_transform()
    test_spruce_tree()
    test_aggregate_json()

    print("\nFull Workflow\n")
    AppFutureManager.new_dir()
    test_full_workflow()
    
    print("\nParallel Workflows\n")
    AppFutureManager.new_dir()
    test_parallel_workflows()

    print("\nOpenAI Function Calls\n")
    AppFutureManager.new_dir()
    agent = OpenAIAgent(functions=functions)
    agent.start_conversation(
    '''
    Help me with two things: 
        First: transform the vcf file ./example_data/VEP_raw.A25.mutect2.filtered.snp.vcf.
        Second: execute pyclone-vi on the file outputed in the first step.
    ''')