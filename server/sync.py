from block import Block
from blockchain import Blockchain
from config import *

import os
import json
import requests
import glob
import sys

def sync_local():
    local_chain = Blockchain()
    local_chain.restore_chain()
    return local_chain

def sync_overall(save = False):
    print(" * Start syncing...")
    best_chain = sync_local()
    best_chain_is_local_chain = True
    for peer in PEERS:
        peer_blockchain_url = peer + 'blockchain.json'
        try:
            r = requests.get(peer_blockchain_url)
            peer_blockchain_dict = r.json()
            print(' * Chain from %s:' % (peer_blockchain_url))
            print(peer_blockchain_dict)
            peer_blocks = []
            for peer_block in peer_blockchain_dict:
                peer_blocks.append(Block(
                    index=peer_block['index'],
                    timestamp=peer_block['timestamp'],
                    transactions=peer_block['transactions'],
                    previous_hash=peer_block['previous_hash'],
                    diff=peer_block['diff'],
                    hash=peer_block['hash'],
                    nonce=peer_block['nonce']
                ))
            peer_blockchain = Blockchain()
            peer_blockchain.chain = peer_blocks
            
            if peer_blockchain.is_valid_chain() and len(peer_blockchain.chain) > len(best_chain.chain):
                best_chain = peer_blockchain
                best_chain_is_local_chain = False
            
        except requests.ConnectionError:
            print("Peer %s is not running and can not be synced" %(peer))
        else:
            print(" * Syncing complete from peer %s" %(peer))

    if not best_chain_is_local_chain:
        best_chain.save()
        
    return best_chain
