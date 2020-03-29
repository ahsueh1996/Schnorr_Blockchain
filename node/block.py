# Native packages
import os
import sys

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
        self.nounce = start_nounce
        self.mining_difficulty = mining_difficulty
        self.timestamp = utils.time_millis()
        self.height = height
        self.is_mined = False
        self.block_hash = None
        
    @classmethod
    def from_mined_block_dict(cls, d):
        new_block =  cls(d[previous_block_hash],
                         d[transactions],
                         d[height],
                         start_nounce = d[nounce],
                         mining_difficulty = sd[mining_difficulty])
        cls.is_mined = True
        cls.block_hash = d[block_hash]
        return cls    

    def block_content_to_dict(self):
        d =  {'timestamp': self.previous_block_hash,
              'nounce': self.nounce,
              'transactions': self.transactions,
              'previous_block_hash': self.previous_block_hash,
              'height': self.height,
              'mining_difficulty': self.mining_difficulty}
        return d
    
    def export_block_to_dict(self):
        return self.block_content_to_dict().update({'block_hash': self.block_hash})

    def hash_block(self):
        return data_hash(dict_to_utf8(self.block_content_to_dict()))

    def mine(self):
        while True:
            progress(self.nounce,0,'Mining block with nounce...')
            guess_hash = self.hash_block()
            if guess_hash[:self.mining_difficulty] == '0'*self.mining_difficulty:
                progress(self.nounce,self.nounce,'Block mined @ {}'.format(guess_hash))
                break
            self.nounce += 1
        self.block_hash = guess_hash
        
    def broadcast_block(self,peers):
        utils.broadcast(self.export_block_to_dict(), peers=peers, route="/peer_gossiped_new_block")        
        
    def is_valid(self):
        true_hash = self.hash_block
        return true_hash == self.block_hash
    
    def __eq__(self, other):
        return self.export_block_to_dict() == other.export_block_to_dict()
    
    def __ne__(self, other):
        return not self.__eq__(other)
