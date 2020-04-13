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
config.NODE_CSV_FILE = "./experiments/exp2.csv"
import utils
from utils import log_info, log_warn, log_error, progress
from node.router import app, blockchain, node_registry, sched, EXIT
from node.block import Block
from node.blockchain import Blockchain
from node.scheduled_routines import SCHED_master_node




if __name__ == '__main__':
    
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    
    ip = requests.get('https://api.ipify.org').text 
    blockchain.update_id_and_peers(999, [], ip=ip+":"+str(port))
    blockchain.pause_mining()

    print('ap schedule starts....')
    sched.start()
    print('Flask starting...')
    sched.add_job(SCHED_master_node, args=[blockchain, sched, node_registry], id='master_node')

    # Now start the flask app in silent mode    
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)        
    app.run(host=node_registry.ip, port=port)
    

    print("\n\n==================== Simulation complete ===============\n\n")
    # collect all blocks from peers
    max_height = len(node_registry.nodemap.keys())
    chain = [utils.ListDict() for h in range(max_height+1)]
    for p, peer in enumerate(blockchain.peers):
        log_info('Processing peer ({})/({}) @ {} ......'.format(p, len(blockchain.peers), peer))
        for h in range(max_height+1):
            log_info('\tGetting block ({}) ......'.format(h))
            response = utils.broadcast(str(h), [peer], "/sync_next_block")
            block_dict = utils.receive(response.data)
            block_hash = block_dict['block_hash']
            block_height = block_dict['height']
            chain[block_height].append(block_hash,block_dict)
    log_info('Chain saved: {}'.format([len(each) for each in chain]))
            
    # visualize and save photo of blockchain
    
    # 