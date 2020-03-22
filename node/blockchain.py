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


class Blockchain:

    def __init__(self):
        self.mining_paused = False
        self.transactions_pool = []
        self.chain = ListDict()
        # Create genesis block
        self.create_genesis_block()
        self.mine()

    def create_genesis_block(self):
        genesis_block = Block(
            previous_block_hash=0,
            transactions=self.transactions,
            height=1)
        genesis_block.mine()
        self.chain[genesis_block.block_hash] = genesis_block
        return

    def mine(self):
        # Restore chain if empty
        if self.chain == []:
            self.restore_chain()
        
        while not self.mining_paused:
            # Put transaction from waiting list into block
            transactions  = []   
            transaction_dir = '../transaction/' + TRANSACTION_DIR
            for i, filename in enumerate(sorted(os.listdir(transaction_dir))):
                with open('%s%s' %(transaction_dir, filename)) as file:
                    transaction = json.load(file)
                    transactions.append(transaction)
            
            transactions=sorted(transactions, key=lambda x: x['value'],reverse=True)
            transactions=transactions[:5]
            
            # Mining block
            latest_block = self.chain[-1]
            next_index = int(latest_block.index) + 1
            next_block = Block(
                index = str(next_index),
                timestamp = date.datetime.now(),
                transactions = transactions,
                previous_hash = latest_block.hash,
                diff = MINING_DIFFICULTY
                    )
            next_block = next_block.mine()
            self.chain.append(next_block)
            next_block.save()
            broadcaster.broadcast_new_block(next_block)
            
            # Remove minned transactions out of waiting list
            for i, filename in enumerate(sorted(os.listdir(transaction_dir))):
                with open('%s%s' %(transaction_dir, filename)) as file:
                    transaction = json.load(file)
                    check =transaction in transactions
                    if check:
                        print('** mine 5 trans' +filename)

                        os.remove('../transaction/'+transaction_dir +filename)
    
    def is_valid_chain(self):
        previous_block = None
        for i, block in enumerate(self.chain):
            if not block.is_valid():
                print(' - Error: block #%s is invalid' % (block.index))
                return False
            
            if i == 0:
                previous_block = block
                
            if i != 0 and previous_block.hash != block.previous_hash:
                print(' - Error: block #%s and block #%s is not linked' %
                      (block.index, previous_block.index))
                print(' - Error: block #%s is invalid' %
                      (block.index))
                return False
            
            if i != 0:
                previous_block = block
        return True

    def __len__(self):
        return len(self.chain)

    def __eq__(self, other):
        if len(self) != len(other):
            return False
        for self_block, other_block in zip(self.chain, other.chain):
            if not self_block == other_block:
                return False
        return True

    def __gt__(self, other):
        return len(self.chain) > len(other.chain)
    
