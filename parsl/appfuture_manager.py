
from time import sleep

from filesystem_util import RUNS_DIR, generate_datetime_subdir

from parsl.dataflow.futures import AppFuture


class AppFutureManager:
    app_counter = 0
    appfuture_map = {}

    def new_future_id(run_function):
        AppFutureManager.app_counter += 1
        return f'future_{AppFutureManager.app_counter}_{run_function.__name__}'

    def index(future_id:str, future:AppFuture) -> str:
        AppFutureManager.appfuture_map[future_id] = future

    def query(future_id:str) -> AppFuture:
        return AppFutureManager.appfuture_map[future_id]
    
    def new_dir():
        AppFutureManager.DIR = generate_datetime_subdir(RUNS_DIR)
        sleep(1)