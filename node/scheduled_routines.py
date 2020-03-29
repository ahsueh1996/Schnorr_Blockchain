# Native packages
import os
import sys
import glob
import datetime
import requests
import random
import apscheduler
from apscheduler.schedulers.blocking import BlockingScheduler

# Project packages
sys.path.append('.')
import config
import utils
from utils import log_info, log_warn, log_error, progress
from node.block import Block
from node.blockchain import Blockchain



def SCHED_mine_for_block(blockchian):
    return blockchian.mint_new_block_and_mine()
    

def SCHED_mine_for_block_listener(event,blockchain):
    # invoke a function to generate more transactions
    amount = random.randint(0,15)
    for i in range(amount):
        new_transaction = blockchain.client.generate_new_random_transaction()
        blockchian.add_transaction(new_transaction)
        new_transaction.broadcast(blockchain.peers)
    # check if the mining job has finished
    if event.job_id == 'mining':
        new_block = event.retval
        if new_block:
            log_info("Minted and Mined new block @ {}".format(new_block.block_hash))
            blockchain.add_block(new_block)
            new_block.broadcast_block(blockchain.peers)
            sched.add_job(mine.mine_for_block, args=[blockchain], id='mining')


def SCHED_validate_and_add_possible_block(possible_block_dict, blockchain):
    possible_block = Block.from_mined_block_dict(possible_block_dict)
    if block.chain.contains_key(possible_block.block_hash):
        log_info('Block arleady in chain')
        return False
    
    if blockchain.validate_possible_block(possible_block):
        blockchain.add_block(possible_block)
        log_info('Accept new block @ {}'.format(possible_block.block_hash))

        # we want to kill and restart the mining block
        try:
            sched.remove_job('mining')
            log_info('Removed "mining" job')
        except apscheduler.jobstores.base.JobLookupError:
            log_info('No "mining" job found')
    
        log_info('Restart "mining" job...')
        sched.add_job(SCHED_mine_for_block, kwargs={
                        'rounds': STANDARD_ROUNDS, 'start_nonce': 0}, id='mining')  # add the block again
        return True
    else:
        log_info('REJECT new block @ {}'.format(possible_block.block_hash))
        return False

def SCHED_validate_and_add_possible_transaction(possible_transaction_dict, blockchain):
    possible_transaction = Transaction.from_transaction_dict(possible_transaction_dict)
    if blockchain.transactions_pool.contains_key(possible_transaction.signature):
        log_info('Transaction arleady in mem pool')
        return False
    
    if blockchain.validate_possible_transaction(possible_transaction):
        blockchain.add_transaction(possible_transaction)
        log_info('Accept new transaction with signature @ {}'.format(possible_block.signature))
        return True
    else:
        log_info('REJECT new transaction with signature @ {}'.format(possible_block.signature))
        return False
