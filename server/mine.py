import sys
import logging
import datetime
import time
import json
import hashlib
import requests
import os
import glob

from block import Block
from blockchain import blockchain
from config import *
from sync import sync
from broadcaster import broadcaster
import utils

import apscheduler
from apscheduler.schedulers.blocking import BlockingScheduler

# if we're running mine.py, we don't want it in the background
# because the script would return after starting. So we want the
# BlockingScheduler to run the code.
sched = BlockingScheduler(standalone=True)

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def mine_for_block(chain=None, rounds=STANDARD_ROUNDS, start_nonce=0, timestamp=None):
    if not chain:
        blockchain.restore_chain()  # gather last node
    prev_block = blockchain.most_recent_block()
    return mine_from_prev_block(prev_block, rounds=rounds, start_nonce=start_nonce, timestamp=timestamp)


def mine_from_prev_block(prev_block, rounds=STANDARD_ROUNDS, start_nonce=0, timestamp=None):
    # create new block with correct
    new_block = utils.create_new_block_from_previous(
        previous_block=prev_block)
    return mine_block(new_block, rounds=rounds, start_nonce=start_nonce)


def mine_block(new_block, rounds=STANDARD_ROUNDS, start_nonce=0):
    print("Mining for block %s. start_nonce: %s, rounds: %s" %
          (new_block.index, start_nonce, rounds))
    # Attempting to find a valid nonce to match the required difficulty
    # of leading zeros. We're only going to try 1000
    nonce_range = [i+start_nonce for i in range(rounds)]
    for nonce in nonce_range:
        new_block.nonce = nonce
        new_block.hash_block()
        if str(new_block.hash[0:MINING_DIFFICULTY]) == '0' * MINING_DIFFICULTY:
            print("block %s mined. Nonce: %s" %
                  (new_block.index, new_block.nonce))
            assert new_block.is_valid()
            return new_block, rounds, start_nonce, new_block.timestamp

    # couldn't find a hash to work with, return rounds and start_nonce
    # as well so we can know what we tried
    return None, rounds, start_nonce, new_block.timestamp


def mine_for_block_listener(event):
    # need to check if the finishing job is the mining
    if event.job_id == 'mining':
        new_block, rounds, start_nonce, timestamp = event.retval
    # if didn't mine, new_block is None
    # we'd use rounds and start_nonce to know what the next
    # mining task should use
    latest_block = blockchain.most_recent_block()
    if new_block and int(latest_block.index) < int(new_block.index):
        print(" * Mined a new block, block hash %s" %(new_block.hash))
        blockchain.add_block(new_block)
        new_block.save()
        print("ăăăăăăăăăă")
        new_block_dict = new_block.to_dict()
        transactions = new_block_dict['transactions']
        
        # Remove minned transactions out of waiting list
        transaction_dir ='../transaction/'+ TRANSACTION_DIR
        for i, filename in enumerate(sorted(os.listdir(transaction_dir))):
            with open('%s%s' %(transaction_dir, filename)) as file:
                transaction = json.load(file)
                check =transaction in transactions
                if check:
                    print('** mine 5 trans' +filename)
    
                    os.remove('../transaction/'+TRANSACTION_DIR +filename)
        




        broadcaster.broadcast_new_block(new_block)
        sched.add_job(mine_from_prev_block, args=[new_block], kwargs={
                      'rounds': STANDARD_ROUNDS, 'start_nonce': 0}, id='mining')  # add the block again
    else:
        # print(event.retval)
        sched.add_job(mine_for_block, kwargs={'rounds': rounds, 'start_nonce': start_nonce +
                                              rounds, 'timestamp': timestamp}, id='mining')  # add the block again
        sched.print_jobs()


def validate_possible_block(possible_block_dict):
    possible_block = Block(
        index=possible_block_dict['index'],
        timestamp=possible_block_dict['timestamp'],
        transactions=possible_block_dict['transactions'],
        previous_hash=possible_block_dict['previous_hash'],
        diff=possible_block_dict['diff'],
        hash=possible_block_dict['hash'],
        nonce=possible_block_dict['nonce']
    )
    
    my_latest_block = blockchain.most_recent_block()
    
    if not possible_block.is_valid():
        return False
    
    if my_latest_block.index >= possible_block.index:
        return False
    
    blockchain.add_block(possible_block)
    possible_block.save()
    # delete trans wait  broadcast
    possible_block.delete_transaction()
    print(' * Accept new block at index %s with hash %s' %
            (possible_block.index, possible_block.hash))

    # we want to kill and restart the mining block so it knows it lost
    sched.print_jobs()
    try:
        sched.remove_job('mining')
        print("removed running mine job in validating possible block")
    except apscheduler.jobstores.base.JobLookupError:
        print("mining job didn't exist when validating possible block")

    print("readding mine for block validating_possible_block")
    print(sched)
    print(sched.get_jobs())
    sched.add_job(mine_for_block, kwargs={
                    'rounds': STANDARD_ROUNDS, 'start_nonce': 0}, id='mining')  # add the block again
    print(sched.get_jobs())

    return True


if __name__ == '__main__':

    sched.add_job(mine_for_block, kwargs={
                  'rounds': STANDARD_ROUNDS, 'start_nonce': 0}, id='mining')  # add the block again
    sched.add_listener(mine_for_block_listener,
                       apscheduler.events.EVENT_JOB_EXECUTED)
    sched.start()
