# Native package
import sys
import Crypto

# Project package
sys.path.append('.')
import config
from utils import *

KEYGEN_ALGO = config.KEYGEN_ALGO

def ppk_keygen():
    if KEYGEN_ALGO=='RSA':
        import binascii
        import Crypto.Random
        from Crypto.PublicKey import RSA
        random_gen = Crypto.Random.new().read
        private_key = RSA.generate(1024, random_gen)
        public_key = private_key.publickey()
        private_key = binascii.hexlify(private_key.exportKey(format='DER'))
        public_key = binascii.hexlify(public_key.exportKey(format='DER'))
    else: 
        log_error("Unknown keygen algo defined")
        

    return public_key, private_key