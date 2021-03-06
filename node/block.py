# Native packages
import os
import sys
from time import sleep

# Project packages
sys.path.append('.')
import config
import utils
from utils import log_info, log_warn, log_error, progress, dynamic_log_level
from security.hash import dict_to_hash


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
        new_block = cls(d["previous_block_hash"],
                        d["transactions"],
                        d["height"],
                        start_nounce = d["nounce"],
                        mining_difficulty = d["mining_difficulty"])
        new_block.is_mined = True
        new_block.block_hash = d["block_hash"]
        new_block.timestamp = d['timestamp']
        return new_block    

    def block_content_to_dict(self):
        d =  {'timestamp': self.timestamp,
              'nounce': self.nounce,
              'transactions': self.transactions,
              'previous_block_hash': self.previous_block_hash,
              'height': self.height,
              'mining_difficulty': self.mining_difficulty}
        return d
    
    def export_block_to_dict(self):
        d = self.block_content_to_dict()
        d.update({'block_hash': self.block_hash})
        return d

    def hash_block(self):
        return dict_to_hash(self.block_content_to_dict())

    def mine(self):
        while True:
            progress(self.nounce,0,'[node.block.Block.mine] Mining block with nounce...')
            guess_hash = self.hash_block()
            if guess_hash[:self.mining_difficulty] == '0'*self.mining_difficulty:
                progress(self.nounce,self.nounce,'[node.block.Block.mine] Block mined @ {}'.format(guess_hash))
                break
            self.nounce += 1
        self.block_hash = guess_hash
        return self
        
    def broadcast_block(self,peers):
        d = self.export_block_to_dict()
        # log_info('[node.block.Block.broadcast_block] broadcasting {} \n........'.format(utils.format_dict_to_str(d)))
        utils.broadcast(d, peers=peers, route="/peer_gossiped_new_block")        
        
    def is_valid(self):
        log_info('[node..Block.is_valid] recorded hash: {}'.format(self.block_hash))
        actual_hash = self.hash_block()
        log_info('[node..Block.is_valid] actual hash: {}'.format(actual_hash))
        return actual_hash == self.block_hash
    
    def __eq__(self, other):
        return self.export_block_to_dict() == other.export_block_to_dict()
    
    def __ne__(self, other):
        return not self.__eq__(other)
