from config import *

import os
import json
import requests
import glob
import sys

class Broadcast():
    def broadcast_new_block(self, block):
        block_dict = block.to_dict()
        print('-----------------------------------')
        print(' * Broadcasting block %s at index %s' %(block_dict['hash'], block_dict['index']))
        
        data = block.to_json()
        for peer in PEERS:
            peer_broadcast_url = peer + 'someone_mined_new_block'
            print(' * Broadcasting to %s' %(peer_broadcast_url))
            try:
                r = requests.post(peer_broadcast_url, data=data)
                print(' * Broadcast successfully to %s' % (peer_broadcast_url))
                print(' * Node %s said: %s' %(peer_broadcast_url, r.content))
            except requests.ConnectionError:
                print(' * Can not broadcast to %s due to connection error' % (peer_broadcast_url))
            
        print('-----------------------------------\n')
        
broadcaster = Broadcast()
