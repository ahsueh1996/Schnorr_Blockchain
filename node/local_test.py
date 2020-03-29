# Native packages
import os
import sys
import glob
import datetime
import requests
import apscheduler
from argparse import ArgumentParser
  


# Project packages
sys.path.append('.')
import config
config.NODE_CSV_FILE = "./node/local_test_node_list.csv"
import utils
from utils import log_info, log_warn, log_error, progress
from router import app, blockchain, node_resistry, sched
from node.block import Block
from node.blockchain import Blockchain
from node.scheduled_routines import SCHED_mine_for_block, SCHED_mine_for_block_listener
from node.node_list import Node_Registry



if __name__ == '__main__':
    t = blockchain.client.generate_random_transaction()    
    log_info(t.content_to_dict)
    log_info("Signing transaction...")
    t.sign_transaction()
    log_info("Verifying transaction...")
    t.verify_transaction()
    
    