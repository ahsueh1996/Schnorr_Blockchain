# Native packages
import os
import sys
import signal
import glob
import datetime
import requests
import apscheduler
from argparse import ArgumentParser

# Project packages
sys.path.append('.')
import config
config.NODE_CSV_FILE = "./node/test2_and_3.csv"
import utils
from utils import log_info, log_warn, log_error, progress
from router import app, blockchain, node_resistry, sched, EXIT
from node.block import Block
from node.blockchain import Blockchain
from node.scheduled_routines import SCHED_mine_for_block, SCHED_mine_for_block_listener

signal.signal(signal.SIGINT, EXIT)
signal.signal(signal.SIGTERM, EXIT)


if __name__ == '__main__':
    
    sched.add_job(SCHED_mine_for_block, args=[blockchain, sched], id='mining')
    sched.add_listener(SCHED_mine_for_block_listener, apscheduler.events.EVENT_JOB_EXECUTED)
    sched.start()
    
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5001, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    
    
    
        
    app.run(host='128.100.241.138', port=port)s