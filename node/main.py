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
import utils
from utils import log_info, log_warn, log_error, progress
from router import app, blockchain, node_resistry, sched
from node.block import Block
from node.blockchain import Blockchain
from node.scheduled_routines import SCHED_mine_for_block, SCHED_mine_for_block_listener
from node.node_list import Node_Registry
from client import client



if __name__ == '__main__':
    

    
    
    sched.add_job(SCHED_mine_for_block, args=[blockchain], id='mining')
    sched.add_listener(SCHED_mine_for_block_listener, apscheduler.events.EVENT_JOB_EXECUTED, args=[blockchain])
    sched.start()
    
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    app.run(host='127.0.0.1', port=port)
