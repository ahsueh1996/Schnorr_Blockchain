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
from node.scheduled_routines import SCHED_master_node, SCHED_start_nodes




if __name__ == '__main__':
    
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    
    
    ip = requests.get('https://api.ipify.org').text 
    blockchain.update_id_and_peers(999, [], ip=ip+":"+str(port))
    blockchain.pause_mining()
    
    input('Ready. Press enter to start all nodes....')
    peers = list(node_registry.nodemap.keys())
    print("Peers: {}".format(peers))
    print('ap schedule starts....')
    sched.start()
    print('Flask starting...')
    sched.add_job(SCHED_start_nodes, args=[peers], id='master_start_all_nodes')
    sched.add_job(SCHED_master_node, args=[blockchain, sched, node_registry], id='master_node')

    # Now start the flask app in silent mode    
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)        
    app.run(host=node_registry.ip, port=port)
    

    print("\n\n==================== Simulation complete ===============\n\n")
    # collect all blocks from peers
    max_height = config.END_OF_CHAIN
    chain = [utils.ListDict() for h in range(max_height+1)]
    for p, peer in enumerate(blockchain.peers):
        print('\n\n--------------------------')
        log_info('Processing peer ({})/({}) @ {} ...'.format(p, len(blockchain.peers), peer))
        idx = 0
        block_height = 0
        while block_height < max_height:
            log_info('\tGetting block ({})/({}) ... latest height obtained: ({})'.format(idx,max_height,block_height))
            response = utils.broadcast(str(idx), [peer], "/sync_next_block")
            if response[0] != None:
                block_dict = utils.receive(response[0])
            else:
                block_dict = None
            if type(block_dict) == dict:
                block_hash = block_dict['block_hash']
                block_height = block_dict['height']
                log_info('(height,hash) = {},\n\t\t{}'.format(block_height,block_hash[0:25]))
                block_dict['height'] = int(block_dict['height'])
                block_dict['timestamp'] = float(block_dict['timestamp'])
                chain[block_height].append(block_hash,block_dict)
            else:
                log_info('invalid...')
            idx = idx + 1
    log_info('Chain saved: {}'.format([len(each) for each in chain]))
    
    consensus = len(chain[-1]) == 1
    log_info('Consensus: {}'.format(consensus))
    
    throughputs = []
    for each in chain[-1]:
        print('\n\n------- back track chain ------')
        total_transactions = len(each['transactions'])
        end_time = each['timestamp']
        start_time = end_time
        # backtrack
        curr = each
        while curr['height'] > 0:
            prev_hash = curr['previous_block_hash']
            log_info('Looking for \n\t\tprev block with hash {}\n\t\t at height ({})'.format(prev_hash[0:25],curr['height']-1))
            curr = chain[curr['height']-1][{prev_hash}]
            total_transactions = total_transactions + len(curr['transactions'])
            start_time = min(start_time, float(curr['timestamp']))
        throughputs.append(total_transactions/(end_time-start_time)*1000)  # throughput in trans per sec
        
    avg_throughput = sum(throughputs)/len(throughputs)
    log_info('Avg throughput: {}'.format(avg_throughput))    
