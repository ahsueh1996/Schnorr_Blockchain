# Native packages
import os
import sys
import datetime

# Project packages
sys.path.append('.')
import block
import config
import utils
from utils import log_info, log_warn, log_error, progress, ListDict
from security.hash import data_hash, dict_to_utf8
from client import Client

BLOCK_LIMIT = config.BLOCK_LIMIT
NOUNCE_DISTANCE = config.NOUNCE_DISTANCE

class Blockchain:

    def __init__(self,chain_id=0, peers=[]):
        self.mining_paused = False
        self.transactions_pool = ListDict()
        self.chain = ListDict()
        # Create genesis block
        self.create_genesis_block()
        self.mine()
        self.chain_id = chain_id
        self.client = Client()
        self.peers = peers

    def create_genesis_block(self):
        genesis_block = Block(
            previous_block_hash=0,
            transactions=[],
            height=1
            mining_difficulty=1
            start_nounce=self.chain_id*NOUNCE_DISTANCE)
        genesis_block.mine()
        self.add_block(genesis_block)
        return

    def mint_new_block_and_mine(self):
        
        if not self.mining_paused:
            # Put transaction from waiting list into block
            chosen_transactions  = self.transactions_pool[0:min(BLOCK_LIMIT,len(self.transactions_pool))]   
            
#           # Create the block
            new_block = Block(previous_block_hash=self.chain[-1].block_hash,
                              transactions=[t.export_transaction_to_dict for t in chosen_transactions],
                              height=self.chain[-1].height+1,
                              start_nounce=self.chain_id*NOUNCE_DISTANCE)
            return new_block.mine()
    
    def validate_possible_transaction(self,new_transaction):
        return new_transaction.verify_transaction()
            
    def add_tranasction(self, new_transaction):
        '''
        This function should not be called on its own. We should schedule it so it does not fight the mining schedule
        '''
        self.transactions_pool.append(new_transaction.signature, new_transaction)
        
    def validate_possible_block(self, new_block):
        if new_block.height > self.height() and new_block.is_valid():
            return True
        else:
            return False
        
    def add_block(self, new_block):
        '''
        This function should not be called on its own. We should schedule it so it does not fight the mining schedule
        '''
        self.chain.append(new_block.block_hash, new_block)
        for transaction in new_block.transactions:
            self.transactions_pool.delete({transaction['hash_id']})

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
    
