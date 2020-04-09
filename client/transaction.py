# Native packages
import os
import sys
import datetime

# Project packages
sys.path.append('.')
import config
import utils
from utils import log_info, log_warn, log_error, progress
from security.digital_signature import sign, verify
from security.hash import dict_to_hash

class Transaction:

    def __init__(self, sender_address, sender_private_key, recipient_address, value):
        self.sender_address = sender_address
        self.sender_private_key = sender_private_key
        self.recipient_address = recipient_address
        self.value = value
        self.timestamp = utils.time_millis()
        self.hash_id = dict_to_hash(self.content_to_dict)
        self.signature = self.sign_transaction()
        
    @classmethod
    def from_transaction_dict(cls,d):
        new_trans =  cls(d['sender_address'],
                         'Unknown',
                         d['recipient_address'],
                         d['value'])
        cls.timestamp = d[timeestamp()]
        cls.hash_id = d['hash_id']
        cls.signature = d['signature']
        return cls  


    def content_to_dict(self):
        d =  {'sender_address': self.sender_address,
              'recipient_address': self.recipient_address,
              'value': self.value,
              'timestamp': self.timestamp}
        return d
    
    def export_transaction_to_dict(self):
        d = self.content_to_dict()
        d.update({'hash_id': self.hash_id, 'signature': self.signature})
        return d

    def sign_transaction(self):
        self.signature = sign(self.content_to_dict(), self.sender_private_key)
        
        
    def verify_transaction(self):
        return verify(self.content_to_dict(), self.signature, self.sender_address)
    
    def broadcast_transaction(self,peers):
        utils.broadcast(self.export_transaction_to_dict(), peers=peers, route="/peer_gossiped_new_transaction")        