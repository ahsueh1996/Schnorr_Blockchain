# Native package
import sys
import Crypto
import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

# Project package
sys.path.append('.')
import config
from utils import *

DIGITAL_SIGNATURE_ALGO = config.DIGITAL_SIGNATURE_ALGO

def sign(msg, sender_private_keyprivate_key):
    private_key = RSA.importKey(binascii.unhexlify(sender_private_key))
    signer = PKCS1_v1_5.new(private_key)
    h = SHA.new(str(self.to_dict()).encode('utf8'))
    return binascii.hexlify(signer.sign(h)).decode('ascii')




def verify(signed_msg):
    return True