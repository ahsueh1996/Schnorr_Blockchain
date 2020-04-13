# Native packages
import os
import sys
import glob
import time
import datetime
import requests
import random
import pickle
import apscheduler
from importlib import reload  

# Project packages
sys.path.append('.')
import config
import utils
from utils import log_info, log_warn, log_error, progress, dynamic_log_level
from node.block import Block
from node.blockchain import Blockchain
from client.transaction import Transaction


def refreash_configs(router):
    router = reload(router)
    from node.router import app, blockchain, node_registry, sched
    return app, blockchain, node_registry, sched


# timer.py https://realpython.com/python-timer/
class TimerError(Exception):
    """A custom exception used to report errors in use of Timer class"""

class Timer:
    def __init__(self):
        self._start_time = None

    def start(self):
        """Start a new timer"""
        if self._start_time is not None:
            raise TimerError(f"Timer is running. Use .stop() to stop it")

        self._start_time = time.perf_counter()

    def stop(self):
        """Stop the timer, and report the elapsed time"""
        if self._start_time is None:
            raise TimerError(f"Timer is not running. Use .start() to start it")

        elapsed_time = time.perf_counter() - self._start_time
        self._start_time = None
        # print(f"Elapsed time: {elapsed_time:0.4f} seconds")
        return elapsed_time
    
    
def sizeof_dict(d):
    d_string = pickle.dumps(d)
    return sys.getsizeof(d_string)