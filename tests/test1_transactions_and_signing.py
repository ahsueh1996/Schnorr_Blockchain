# Native packages
import os
import sys
import glob
import datetime
import requests
import apscheduler
from argparse import ArgumentParser
from importlib import reload  
  


# Project packages
sys.path.append('.')
import config
config.NODE_CSV_FILE = "./tests/test2_and_3.csv"
import utils
from utils import log_info, log_warn, log_error, progress
from experiments import exp_utils
import node.router as router
from node.block import Block
from node.blockchain import Blockchain
from node.scheduled_routines import SCHED_mine_for_block, SCHED_mine_for_block_listener
from node.node_list import Node_Registry



if __name__ == '__main__':
    print('================')
    log_info("[FROM MAIN] Using ECDSA")
    print('================')
    config.DIGITAL_SIGNATURE_ALGO = 'ECDSA'
    app, blockchain, node_resistry, sched = exp_utils.refreash_configs(router)
    t = blockchain.client.generate_random_transaction()    
    log_info("[FROM MAIN] Signing transaction...")
    t.sign_transaction()
    log_info("[FROM MAIN] Verifying transaction...")
    t.verify_transaction()
    log_info("[FROM MAIN] Verifying sabotaged tansaction...")
    t.timestamp = utils.time_millis()
    log_info("[FROM MAIN] sabatoged transaction: \n{}".format(utils.format_dict_to_str(t.content_to_dict())))
    t.verify_transaction()
    
    print('\n\n')
    log_info("[FROM MAIN] ECDSA Wallets")
    print('================')
    for i,wallet in enumerate(blockchain.client.wallets):
        progress(i, i, "[FROM MAIN] wallet: \n{}".format(utils.format_dict_to_str(wallet)))
    
    
    print('\n\n\n\n\n===============')
    log_info("[FROM MAIN] Using SCHNORR")
    print('================')
    config.DIGITAL_SIGNATURE_ALGO = 'SCHNORR'
    app, blockchain, node_resistry, sched = exp_utils.refreash_configs(router)
    t = blockchain.client.generate_random_transaction()    
    log_info("[FROM MAIN] Signing transaction...")
    t.sign_transaction()
    log_info("[FROM MAIN] Verifying transaction...")
    t.verify_transaction()
    log_info("[FROM MAIN] Verifying sabotaged tansaction...")
    t.timestamp = utils.time_millis()
    log_info("[FROM MAIN] sabatoged transaction: \n{}".format(utils.format_dict_to_str(t.content_to_dict())))
    t.verify_transaction()
    
    print('\n\n')
    log_info("[FROM MAIN] SCHNORR Wallets")
    print('================')
    for i,wallet in enumerate(blockchain.client.wallets):
        progress(i, i, "[FROM MAIN] wallet: \n{}".format(utils.format_dict_to_str(wallet)))
    
    
