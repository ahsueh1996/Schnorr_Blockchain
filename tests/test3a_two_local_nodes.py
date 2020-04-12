# Native packages
import os
import sys
import signal
import glob
import datetime
import logging
import requests
import apscheduler
from argparse import ArgumentParser

# Project packages
sys.path.append('.')
import config
config.NODE_CSV_FILE = "./tests/test2_and_3.csv"
import utils
from utils import log_info, log_warn, log_error, progress
from node.router import app, blockchain, node_resistry, sched, EXIT
from node.block import Block
from node.blockchain import Blockchain
from node.scheduled_routines import SCHED_mine_for_block, SCHED_mine_for_block_listener




if __name__ == '__main__':
    
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    
    node_resistry.set_port_and_update(port)
    blockchain.update_id_and_peers(node_resistry.id, node_resistry.peers)
    
    sched.add_job(SCHED_mine_for_block, args=[blockchain, sched], id='mining')
    sched.add_listener(SCHED_mine_for_block_listener, apscheduler.events.EVENT_JOB_EXECUTED)
    sched.start()

    # Now start the flask app in silent mode    
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)        
    app.run(host=node_resistry.ip, port=port)