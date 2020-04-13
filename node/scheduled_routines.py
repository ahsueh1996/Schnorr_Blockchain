# Native packages
import os
import sys
import glob
import datetime
import requests
import random
import apscheduler
import flask

# Project packages
sys.path.append('.')
import config
import utils
from utils import log_info, log_warn, log_error, progress, dynamic_log_level
from node.block import Block
from node.blockchain import Blockchain
from client.transaction import Transaction

def SCHED_do_none(blockchain, sched):
    return {'sched': sched, 'blockchain': blockchain,}

def SCHED_mine_for_block(blockchain, sched):
    random_id = random.randint(0,1000)    
    log_info("[SCHED_mine_for_block]({}) Starting routine... ".format(random_id))
    return {'sched': sched, 'blockchain': blockchain, 'new_block': blockchain.mint_new_block_and_mine()}
    

def SCHED_mine_for_block_listener(event):
    random_id = random.randint(0,1000)
    log_info("[SCHED_mine_for_block_listener]({}) Event '{}' finished... ".format(random_id, event.job_id))
    e_return = event.retval
    blockchain = e_return['blockchain']    
    if event.job_id =='my_idle' and blockchain.mining_paused:
        sched = e_return['sched']    
        sched.add_job(SCHED_do_none, args=[blockchain, sched], id='my_idle')
        return 'idle'
        
    current_height = blockchain.chain[[-1]][0].height
    log_info("[SCHED_mine_for_block_listener]({}) Current height {}/{} ... ".format(random_id, current_height, config.END_OF_CHAIN))
    if  current_height >= config.END_OF_CHAIN:
        dynamic_log_level.reset_user_log_level()
        log_info("[SCHED_mine_for_block_listener]({}) END OF CHAIN reached. ".format(random_id))
        if config.MASTER != None:
            log_info("[SCHED_mine_for_block_listener]({}) Posting to Master @ {} ".format(random_id, config.MASTER))
            utils.broadcast(blockchain.node_ip, [config.MASTER], "/node_finished")
        else:
            log_info("[SCHED_mine_for_block_listener]({}) Nothing to do.... hanging... ".format(random_id))
        return "END OF MINING..."
    
    if event.job_id == 'mining' or 'possible_block' in event.job_id:
        # invoke a function to generate more transactions
        amount = random.randint(0,config.TRANSACTION_RATE)
        log_info("[SCHED_mine_for_block_listener]({}) Make some new transactions.. ".format(random_id))
        # dynamic_log_level.set_log_level(0)
        for i in range(amount):
            new_transaction = blockchain.client.generate_random_transaction()
            blockchain.add_transaction(new_transaction)
            new_transaction.broadcast_transaction(blockchain.peers)
        # dynamic_log_level.reset_user_log_level()
        # check if the mining job has finished        
        
    if event.job_id == 'mining':
        new_block = e_return['new_block']
        sched = e_return['sched']        
        if new_block:
            log_info("[SCHED_mine_for_block_listener]({}) Minted and Mined new block @ {}".format(random_id, new_block.block_hash))
            blockchain.add_block(new_block)
            new_block.broadcast_block(blockchain.peers)
            sched.add_job(SCHED_mine_for_block, args=[blockchain, sched], id='mining')
        else: 
            log_info("[SCHED_mine_for_block_listener]({}) Mining returned {}".format(random_id, new_block))

def SCHED_validate_and_add_possible_block(possible_block_dict, blockchain, sched, random_id):
    if not random_id:
        random_id = random.randint(0,1000)
    log_info("[SCHED_validate_and_add_possible_block]({}) Starting routine... ".format(random_id))
    possible_block = Block.from_mined_block_dict(possible_block_dict)
    if blockchain.chain.contains_key(possible_block.block_hash):
        log_info('[SCHED_validate_and_add_possible_block]({}) Block arleady in chain'.format(random_id))
        return {'validation': False, 'blockchain': blockchain}
    
    if blockchain.validate_possible_block(possible_block):
        log_info('[SCHED_validate_and_add_possible_block]({}) Accept new block @ {}'.format(random_id, possible_block.block_hash))
        blockchain.add_block(possible_block)
        

        # we want to kill and restart the mining block
        try:
            log_info('[SCHED_validate_and_add_possible_block]({}) Removing "mining" job...'.format(random_id))
            sched.remove_job('mining')
        except apscheduler.jobstores.base.JobLookupError:
            log_info('[SCHED_validate_and_add_possible_block]({}) No "mining" job found'.format(random_id))
    
        log_info('[SCHED_validate_and_add_possible_block]({}) Restart "mining" job...'.format(random_id))
        sched.add_job(SCHED_mine_for_block, args=[blockchain, sched], id='mining')
        return {'validation': True, 'blockchain': blockchain}
    else:
        log_info('[SCHED_validate_and_add_possible_block]({}) REJECT new block @ {}'.format(random_id, possible_block.block_hash))
        return {'validation': False, 'blockchain': blockchain}

def SCHED_validate_and_add_possible_transaction(possible_transaction_dict, blockchain, random_id):
    if not random_id:
        random_id = random.randint(0,1000)
    log_info("[SCHED_validate_and_add_possible_transaction]({}) Starting routine... ".format(random_id))
    possible_transaction = Transaction.from_transaction_dict(possible_transaction_dict)
    if blockchain.transactions_pool.contains_key(possible_transaction.signature):
        log_info('[SCHED_validate_and_add_possible_transaction]({}) Transaction arleady in mem pool'.format(random_id))
        return {'validation': False, 'blockchain': blockchain}
    
    if blockchain.validate_possible_transaction(possible_transaction):
        blockchain.add_transaction(possible_transaction)
        log_info('[SCHED_validate_and_add_possible_transaction]({}) Accept new transaction with signature @ {}'.format(random_id, possible_transaction.signature))
        return {'validation': True, 'blockchain': blockchain}
    else:
        log_info('[SCHED_validate_and_add_possible_transaction]({}) REJECT new transaction with signature @ {}'.format(random_id, possible_transaction.signature))
        return {'validation': False, 'blockchain': blockchain}
    
    
def SCHED_master_node(blockchain, sched, node_registry):
    random_id = random.randint(0,1000)
    log_info("[SCHED_master_node]({}) Checking if finish flag received form all nodes... ".format(random_id))
    received = len(blockchain.peers)
    total_expected = len(node_registry.nodemap.keys())
    if  received >= total_expected:
        log_info("[SCHED_master_node]({}) All nodes finished, attempt flask and sched shutdown... ".format(random_id))
        ''' Allow experiment to take over '''
        try:
            utils.broadcast("shutdown_attempt", [blockchain.node_ip], "/flask_shutdown")
            sched.shutdown()
            log_warn("sched shutdown (ok)")
        except apscheduler.schedulers.SchedulerNotRunningError:
            log_warn("sched shutdown (not ok)")
            pass
    else:
        log_info("[SCHED_master_node]({}) {}/{} received. ".format(random_id,received,total_expected))
    return ""
