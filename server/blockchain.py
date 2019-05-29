'''
title           : blockchain.py
description     : A blockchain implemenation
author          : Adil Moujahid
date_created    : 20180212
date_modified   : 20180309
version         : 0.5
usage           : python blockchain.py
                  python blockchain.py -p 5000
                  python blockchain.py --port 5000
python_version  : 3.6.1
Comments        : The blockchain implementation is mostly based on [1]. 
                  I made a few modifications to the original code in order to add RSA encryption to the transactions 
                  based on [2], changed the proof of work algorithm, and added some Flask routes to interact with the 
                  blockchain from the dashboards
References      : [1] https://github.com/dvf/blockchain/blob/master/blockchain.py
                  [2] https://github.com/julienr/ipynb_playground/blob/master/bitcoin/dumbcoin/dumbcoin.ipynb
'''

from collections import OrderedDict

import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4

import requests
import os
import datetime as date
import glob
import sys

from config import *
from block import Block
from broadcaster import broadcaster

class Blockchain:

    def __init__(self):
        self.mining_paused = False
        self.transactions = []
        self.chain = []
        self.nodes = set()
        # Generate random number to be used as node_id
        self.node_id = str(uuid4()).replace('-', '')
        # Create genesis block
        # self.create_block(0, '00')

    def register_node(self, node_url):
        """
        Add a new node to the list of nodes
        """
        # Checking node_url has valid format
        parsed_url = urlparse(node_url)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')

    def create_genesis_block(self):
        genesis_block = Block(
            index = '0',
            timestamp = date.datetime.now(),
            transactions = [],
            previous_hash = '',
            diff = MINING_DIFFICULTY)
        genesis_block = genesis_block.mine()
        genesis_block.save()
        self.chain.append(genesis_block)
        return genesis_block

    def mining(self):
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
            
    def start(self):
        chaindata_dir = CHAINDATA_DIR
        # check if chaindata folder existed, create if not
        if not os.path.exists(chaindata_dir):
            os.mkdir(chaindata_dir)

        # Create genesis block if no block created before
        if os.listdir(chaindata_dir) == []:
            genesis_block = self.create_genesis_block()
            genesis_block.save()

        self.mining()

    def restore_chain(self):
        chaindata_dir = CHAINDATA_DIR
        total_block = 0
        previous_block = None
        temp_chain = []
        for i, filename in enumerate(sorted(os.listdir(chaindata_dir))):
            with open('%s%s' %(CHAINDATA_DIR, filename)) as file:
                block_data = json.load(file)
                current_block = Block(
                    index = block_data['index'],
                    timestamp = block_data['timestamp'],
                    transactions = block_data['transactions'],
                    previous_hash = block_data['previous_hash'],
                    diff = block_data['diff'],
                    hash = block_data['hash'],
                    nonce = block_data['nonce']
                )
                file.close()
                if not current_block.is_valid():
                    print(' - Error: current block is invalid')
                    print(' - Error: block #%s is invalid' % (block_data['index']))
                    sys.exit()
                
                if i == 0:
                    previous_block = current_block
                    
                if i != 0 and previous_block.hash != current_block.previous_hash:
                    print(' - Error: block #%s and block #%s is not linked' % (current_block.index, previous_block.index))
                    print(' - Error: block #%s is invalid' %
                          (block_data['index']))
                    sys.exit()
                
                if i != 0:
                    previous_block = current_block
                
                temp_chain.append(current_block)
                total_block += 1
        if len(self.chain) < len(temp_chain):
            self.chain = temp_chain
            print(' - Restore chain successfully!')
            print(' - Total block: %s' %(total_block))
            return True
        return False
        
    def save(self):
        for block in self.chain:
            block.save()
        return True
    
    def find_block_by_index(self, index):
        if len(self.chain) <= index:
            return self.chain[index]
        return False
    
    def find_block_by_hash(self, hash):
        for block in self.chain:
            if block.hash == hash:
                return block
        
        return False

    def add_block(self, block):
        self.chain.append(block)
        return True
    
    def block_list_dict(self):
        return [block.to_dict() for block in self.chain]
    
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

    def most_recent_block(self):
        if len(self.chain) > 0:
            return self.chain[-1]
        return self.create_genesis_block()
    
    def __len__(self):
        return len(self.chain)

    def __eq__(self, other):
        if len(self) != len(other):
            return False
        for self_block, other_block in zip(self.chain, other.chain):
            if not self_block == other_block:
                return False

        return True

    def __gt_(self, other):
        return len(self.chain) > len(other.chain)
    
# Instantiate the Blockchain
blockchain = Blockchain()
