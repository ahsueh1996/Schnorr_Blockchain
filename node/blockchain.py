# Native packages
import os
import sys
import datetime

# Project packages
sys.path.append('.')
import config
import utils
from utils import log_info, log_warn, log_error, progress, ListDict, dynamic_log_level
from client.client import Client
from client.transaction import Transaction
from node.block import Block

BLOCK_LIMIT = config.BLOCK_LIMIT
NOUNCE_DISTANCE = config.NOUNCE_DISTANCE

class Blockchain:

    def __init__(self,chain_id=0, peers=[], ip="n/a"):
        self.mining_paused = False
        self.transactions_pool = ListDict()
        self.chain = ListDict()
        self.chain_id = chain_id
        self.node_ip = ip
        self.client = Client()
        self.peers = peers
        self.block_limit = BLOCK_LIMIT
        self.nounce_distance = NOUNCE_DISTANCE
        self.create_genesis_block()
        log_info("[node.blockchain.Blockchain.__init__] Blockchain created")

        
    def pause_mining(self):
        self.mining_paused = True
        
    def resume_mining(self):
        self.mining_paused = False
        
    def update_id_and_peers(self, chain_id, peers, ip):
        self.chain_id = chain_id
        self.peers = peers
        self.node_ip = ip

    def create_genesis_block(self):
        genesis_block = Block(
            previous_block_hash=0,
            transactions=[],
            height=0,
            mining_difficulty=1,
            start_nounce=self.chain_id*self.nounce_distance)
        genesis_block.mine()
        self.add_block(genesis_block)
        return

    def mint_new_block_and_mine(self):
        
        if not self.mining_paused:
            # Put transaction from waiting list into block
            try:
                chosen_transactions  = self.transactions_pool[0:min(self.block_limit,len(self.transactions_pool))]
                if type(chosen_transactions) == type(Transaction):
                    chosen_transactions = [chosen_transactions]
            except IndexError:
                chosen_transactions = []
            
#           # Create the block
            prev_block = self.chain[[-1]][0]
            new_block = Block(previous_block_hash=prev_block.block_hash,
                              transactions=[t.export_transaction_to_dict() for t in chosen_transactions],
                              height=prev_block.height+1,
                              start_nounce=self.chain_id*NOUNCE_DISTANCE)
            log_info('[node..Blockchain.mint_new_block_and_mine] Minted block has ({}) transactions. Mining...'\
                     .format(len(chosen_transactions)))
            # dynamic_log_level.set_log_level(0)
            new_block.mine()
            # dynamic_log_level.reset_user_log_level()
            log_info('[node..Blockchain.mint_new_block_and_mine] Block mined @ {}'.format(new_block.block_hash))
            return new_block
    
    def validate_possible_transaction(self,new_transaction):
        return new_transaction.verify_transaction()
            
    def add_transaction(self, new_transaction):
        '''
        This function should not be called on its own. We should schedule it so it does not fight the mining schedule
        '''
        self.transactions_pool.append(new_transaction.signature, new_transaction)
        
    def validate_possible_block(self, new_block):
        log_info('[node..Blockchain.validate_possible_block] Validating block....')
        is_newer = (new_block.height > self.chain[[-1]][0].height)
        log_info('[node..Blockchain.validate_possible_block] New block is newer: {}'.format(is_newer))
        is_valid = new_block.is_valid()
        log_info('[node..Blockchain.validate_possible_block] New block is valid: {}'.format(is_valid))
        if is_newer and is_valid:
            return True
        else:
            return False
        
    def add_block(self, new_block):
        '''
        This function should not be called on its own. We should schedule it so it does not fight the mining schedule
        '''
        self.chain.append(new_block.block_hash, new_block)
        for transaction in new_block.transactions:
            key = transaction['signature']
            if self.transactions_pool.contains_key(key):
                self.transactions_pool.delete({key})

    def __len__(self):
        return len(self.chain)
    
    def height(self):
        return self.chain[-1].height

    def __eq__(self, other):
        if len(self) != len(other):
            return False
        for self_block, other_block in zip(self.chain, other.chain):
            if not self_block == other_block:
                return False
        return True

    def __gt__(self, other):
        return len(self.chain) > len(other.chain)
    
