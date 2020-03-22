# Native packages
import os
import sys
import datetime

# Project packages
sys.path.append('.')
import config
import utils
from utils import log_info, log_warn, log_error, progress
from security.hash import data_hash, dict_to_utf8


class Block:
    def __init__(self, previous_block_hash, transactions, height, start_nounce=0, mining_difficulty=config.MINING_DIFFICULTY):
        self.previous_block_hash = previous_block_hash
        self.transactions = transactions
        self.nonce = start_nounce
        self.mining_difficulty = mining_difficulty
        self.timestamp = datetime.timestamp()
        self.height = height
        self.is_mined = False
        self.block_hash = None


    def block_content_to_dict(self):
        d =  {'timestamp': self.previous_block_hash,
              'nounce': self.nonce,
              'transactions': self.transactions,
              'previous_block_hash': self.previous_block_hash}
        return d
    
    def export_block_to_dict(self):
        return self.msg_to_dict().update({'block_hash': self.block_hash})

    def hash_block(self):
        return data_hash(dict_to_utf8(self.block_to_dict()))

    def mine(self):
        while True:
            progress(self.nounce,0,'Mining block with nounce...')
            guess_hash = self.hash_block()
            if guess_hash[:self.mining_difficulty] == '0'*self.mining_difficulty:
                progress(self.nounce,self.nounce,'Block mined @ {}'.format(guess_hash))
                break
            self.nonce += 1
        self.block_hash = guess_hash

    def delete_block_transaction_from_pool(self, transactions_pool):
        # Remove mined transactions out of waiting list
        remaining = len(transactions_pool)-1
        curr = 0
        transactions_in_block = [transaction['hash_id'] for transaction in self.transactions]
        while curr <= remaining:
            if transactions_pool[curr].hash_id in transactions_in_block:
                del(transactions_pool[curr])
                remaining -= 1
            else: 
                curr += 1
        return transactions_pool
        
    def is_valid(self):
        true_hash = self.hash_block
        return true_hash == self.block_hash
    
    def __eq__(self, other):
        return self.export_block_to_dict() == other.export_block_to_dict()
    
    def __ne__(self, other):
        return not self.__eq__(other)
