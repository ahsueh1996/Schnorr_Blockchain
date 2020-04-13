# Native packages
import os
import sys
import glob
import random
import datetime
import requests
import apscheduler
from argparse import ArgumentParser
from importlib import reload  
  


# Project packages
sys.path.append('.')
import config
config.NODE_CSV_FILE = "./experiments/exp1.csv"
import node.router as router
import utils
from utils import log_info, log_warn, log_error, progress, dynamic_log_level
from experiments import exp_utils
from node.block import Block
from node.blockchain import Blockchain
from node.scheduled_routines import SCHED_mine_for_block, SCHED_mine_for_block_listener
from node.node_list import Node_Registry

N = 1000
sabotage_rate = 0.7

if __name__ == '__main__':
    print('================')
    log_info("[FROM MAIN] Using ECDSA")
    print('================')
    config.DIGITAL_SIGNATURE_ALGO = 'ECDSA'
    app, blockchain, node_registry, sched = exp_utils.refreash_configs(router)
    
    log_info("[FROM MAIN] Generating {} transactions...".format(N))
    dynamic_log_level.set_log_level(config.IGNORE)
    transactions = []
    for i in range(N):
        transactions.append(blockchain.client.generate_random_transaction())
    dynamic_log_level.reset_user_log_level()
    log_info("[FROM MAIN] Signing transaction...")
    dynamic_log_level.set_log_level(config.IGNORE)
    timer = exp_utils.Timer()
    timer.start()
    for t in transactions:
        t.sign_transaction()
    total_elapsed = timer.stop()
    dynamic_log_level.reset_user_log_level()    
    log_info("[FROM MAIN] Signing {} transactions took {}s or average {}s/transaction".format(N,total_elapsed,total_elapsed/N))
    log_info("[FROM MAIN] Sabotaging transaction with a rate of {}...".format(sabotage_rate))
    sabotaged = []
    for i,t in enumerate(transactions):
        if random.random() > sabotage_rate:
            t.timestamp = utils.time_millis()
            sabotaged.append(i)
    log_info("[FROM MAIN] Verifying {} transactions at sabotage rate of {}...".format(N, sabotage_rate))
    dynamic_log_level.set_log_level(config.IGNORE)
    timer.start()
    for t in transactions:
        t.verify_transaction()
    total_elapsed = timer.stop()
    dynamic_log_level.reset_user_log_level()    
    log_info("[FROM MAIN] Verifying {} transactions took {}s or average {}s/transaction".format(N,total_elapsed,total_elapsed/N))
    log_info("[FROM MAIN] Verifying {} transactions at sabotage rate of {}...".format(N, sabotage_rate))
    dynamic_log_level.set_log_level(config.IGNORE)
    incorrect = 0
    for i,t in enumerate(transactions):
        res = t.verify_transaction()
        if res:
            if i in sabotaged:
                incorrect = incorrect + 1
        else:
            if i not in sabotaged:
                incorrect = incorrect + 1
    dynamic_log_level.reset_user_log_level()    
    log_info("[FROM MAIN] {}/{} transactions verified incorrectly".format(incorrect,N))
    
    
    log_info("[FROM MAIN] Testing size of block...")
    dynamic_log_level.set_log_level(config.IGNORE)
    for t in transactions:
        blockchain.add_transaction(t)
    L = [0, 50, 200, 1000]
    sizes = []
    for l in L:
        blockchain.block_limit = l
        block = blockchain.mint_new_block_and_mine()
        sizes.append(exp_utils.sizeof_dict(block.export_block_to_dict()))
    dynamic_log_level.reset_user_log_level()
    for l,s in zip(L,sizes):
        log_info("[FROM MAIN] Block Limit {} => {} bytes".format(l,s))
    
    print('\n\n')
    print('================')
    log_info("[FROM MAIN] Using SCHNORR")
    print('================')
    config.DIGITAL_SIGNATURE_ALGO = 'SCHNORR'
    app, blockchain, node_registry, sched = exp_utils.refreash_configs(router)
    
    log_info("[FROM MAIN] Generating {} transactions...".format(N))
    dynamic_log_level.set_log_level(config.IGNORE)
    transactions = []
    for i in range(N):
        transactions.append(blockchain.client.generate_random_transaction())
    dynamic_log_level.reset_user_log_level()
    log_info("[FROM MAIN] Signing transaction...")
    dynamic_log_level.set_log_level(config.IGNORE)
    timer = exp_utils.Timer()
    timer.start()
    for t in transactions:
        t.sign_transaction()
    total_elapsed = timer.stop()
    dynamic_log_level.reset_user_log_level()    
    log_info("[FROM MAIN] Signing {} transactions took {}s or average {}s/transaction".format(N,total_elapsed,total_elapsed/N))
    log_info("[FROM MAIN] Sabotaging transaction with a rate of {}...".format(sabotage_rate))
    sabotaged = []
    for i,t in enumerate(transactions):
        if random.random() > sabotage_rate:
            t.timestamp = utils.time_millis()
            sabotaged.append(i)
    log_info("[FROM MAIN] Verifying {} transactions at sabotage rate of {}...".format(N, sabotage_rate))
    dynamic_log_level.set_log_level(config.IGNORE)
    timer.start()
    for t in transactions:
        t.verify_transaction()
    total_elapsed = timer.stop()
    dynamic_log_level.reset_user_log_level()    
    log_info("[FROM MAIN] Verifying {} transactions took {}s or average {}s/transaction".format(N,total_elapsed,total_elapsed/N))
    log_info("[FROM MAIN] Verifying {} transactions at sabotage rate of {}...".format(N, sabotage_rate))
    dynamic_log_level.set_log_level(config.IGNORE)
    incorrect = 0
    for i,t in enumerate(transactions):
        res = t.verify_transaction()
        if res:
            if i in sabotaged:
                incorrect = incorrect + 1
        else:
            if i not in sabotaged:
                incorrect = incorrect + 1
    dynamic_log_level.reset_user_log_level()    
    log_info("[FROM MAIN] {}/{} transactions verified incorrectly".format(incorrect,N))
    
    log_info("[FROM MAIN] Testing size of block...")
    dynamic_log_level.set_log_level(config.IGNORE)
    for t in transactions:
        blockchain.add_transaction(t)
    L = [0, 50, 200, 1000]
    sizes = []
    for l in L:
        blockchain.block_limit = l
        block = blockchain.mint_new_block_and_mine()
        sizes.append(exp_utils.sizeof_dict(block.export_block_to_dict()))
    dynamic_log_level.reset_user_log_level()
    for l,s in zip(L,sizes):
        log_info("[FROM MAIN] Block Limit {} => {} bytes".format(l,s))

    