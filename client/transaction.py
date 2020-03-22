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
from security.hash import data_hash, dict_to_utf8

class Transaction:

    def __init__(self, sender_address, sender_private_key, recipient_address, value):
        self.sender_address = sender_address
        self.sender_private_key = sender_private_key
        self.recipient_address = recipient_address
        self.value = value
        self.timestamp = datetime.timestamp()
        self.hash_id =None
        self.hash_id = data_hash(dict_to_utf8(self.msg_transaction_to_dict))
        self.signature = self.sign_transaction()


    def msg_to_dict(self):
        d =  {'sender_address': self.sender_address,
              'recipient_address': self.recipient_address,
              'value': self.value,
              'timestamp': self.timestamp}
        return d
    
    def export_transaction_to_dict(self):
        return self.msg_to_dict().update({'hash_id': self.hash_id, 'signature': self.signature})

    def sign_transaction(self):
        self.signature = sign(msg_to_dict, self.sender_private_key)
        
        
    @staticmethod
    def verify_transaction(signed_transaction):
        return verify(signed_transaction)
        