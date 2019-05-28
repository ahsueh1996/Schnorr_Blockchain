import hashlib as hasher
import datetime as date
# import config as conf
import json
import sys
import os
from config import *


class Block:
    def __init__(self, **kwargs):
        if not kwargs.keys() & BLOCK_VAR_CONVERSIONS:
            raise ValueError
        self.index = kwargs['index']
        self.timestamp = kwargs['timestamp']
        self.previous_hash = kwargs['previous_hash']
        self.transactions = kwargs['transactions']
        self.diff = kwargs['diff']

        if 'nonce' in kwargs:
            self.nonce = kwargs['nonce']
        else:
            self.nonce = 0

        if 'hash' in kwargs:
            self.hash = kwargs['hash']
        else:
            self.hash = ''

    def mine(self):
        hash_and_nonce = self.proof_of_work()
        self.hash = hash_and_nonce['hash']
        self.nonce = hash_and_nonce['nonce']
        return self

    def hash_block(self):
        sha = hasher.sha256()
        data = (str(self.index) + str(self.timestamp) + str(self.transactions) +
                str(self.previous_hash) + str(self.diff) + str(self.nonce)).encode('utf-8')
        sha.update(data)
        self.hash = sha.hexdigest()
        return self.hash

    def proof_of_work(self):

        print(" - Start mining")
        diff = MINING_DIFFICULTY
        true_hash = ''

        while True:
            guess_hash = self.hash_block()
            # print(" - Mining: %s" % guess_hash)
            if guess_hash[:diff] == '0'*diff:
                true_hash = guess_hash
                print(" - Mine successfully")
                print(" - Mined hash: %s" % true_hash)
                break
            self.nonce += 1

        return {'hash': true_hash, 'nonce': self.nonce}

    def save(self):
        index_string = str(self.index).zfill(6)
        filename = '%s%s.json' % (CHAINDATA_DIR, index_string)
        print(" - New block saved to %s" % (filename))
        data = self.to_dict()
        file = open(filename, 'w')
        file.write(json.dumps(data, indent=4))
        file.close()

    def to_dict(self):
        block_data = {}
        block_data['index'] = str(self.index)
        block_data['hash'] = str(self.hash)
        block_data['previous_hash'] = str(self.previous_hash)
        block_data['timestamp'] = str(self.timestamp)
        block_data['transactions'] = self.transactions
        block_data['diff'] = str(self.diff)
        block_data['nonce'] = str(self.nonce)

        return block_data

    def to_json(self):
        return json.dumps(self.to_dict())
        
    def is_valid(self):
        block_hash = self.hash
        guess_hash = self.hash_block()
        return guess_hash == block_hash
    
    def __eq__(self, other):
        return (self.index == other.index and
                self.timestamp == other.timestamp and
                self.previous_hash == other.previous_hash and
                self.hash == other.hash and
                self.nonce == other.nonce and
                self.transactions == other.transactions)
    
    def __ne__(self, other):
        return not self.__eq__(other)
