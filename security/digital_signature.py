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
from security.hash import data_hash, dict_to_utf8
from security.schnorr import schnorr_sign, schnorr_verify

DIGITAL_SIGNATURE_ALGO = config.DIGITAL_SIGNATURE_ALGO

def sign(msg, sender_private_key):
    
    h = data_hash(dict_to_utf8(msg))
    
    if DIGITAL_SIGNATURE_ALGO == 'ECDSA':
        private_key = RSA.importKey(binascii.unhexlify(sender_private_key))
        signer = PKCS1_v1_5.new(private_key)
        return binascii.hexlify(signer.sign(h)).decode('ascii')
    
    elif DIGITAL_SIGNATURE_ALGO == 'SCHNORR':
        sender_address = "DD308AFEC5777E13121FA72B9CC1B7CC0139715309B086C960E18FD969774EB8"
        private_key_tmp = "C90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B14E5C9"
        return = binascii.hexlify(schnorr_sign(h, sender_private_key)).decode('ascii')
    else:
        log_error("Unkown DSA in config -- cannot create digital signature!")




def verify(msg, signature, sender_public_key):
    if DIGITAL_SIGNATURE_ALGO == 'ECDSA':
        public_key_2 = RSA.importKey(binascii.unhexlify(public_key))
		
        verifier = PKCS1_v1_5.new(public_key_2)
        print("verification = ", verifier)
			
        transaction = OrderedDict({'sender_address': public_key, 
                                'recipient_address': "100",
                                'value': value})
        print("================ Transaction = ", Transaction)
			
        h = SHA.new(str(transaction).encode('utf8'))
        print("================ h = ", h)
        print("verification = ", verifier.verify(h, binascii.unhexlify(signature)))
    elif DIGITAL_SIGNATURE_ALGO == 'SCHNORR':    
        return = schnorr_verify(msg, sender_public_key, signature)
    else:
        log_error("Unknown DSA in config -- cannot verify signature!")