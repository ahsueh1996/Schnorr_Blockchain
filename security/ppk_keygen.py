# Native package
import os
import sys
import Crypto


# Project package
sys.path.append('.')
import config
import security.schnorr as schnorr
from security.hash import bytes_to_hex, hex_to_bytes
from utils import *
from ellipticcurve.privateKey import PrivateKey
from ellipticcurve.publicKey import PublicKey


def ppk_keygen():
    '''
    PEM (string)
    DER
    Bytes
    formats
    '''
    if config.DIGITAL_SIGNATURE_ALGO == 'ECDSA':
        # https://github.com/starkbank/ecdsa-python
        '''
        MUST use toPem....
        private_key = PrivateKey()
        private_key.toPem() == PrivateKey.fromPem(private_key.toPem()).toPem()
        type(private_key.toPem()) == str
        public_key.toPem() == PublicKey.fromPem(public_key.toPem()).toPem()
        '''
        private_key = PrivateKey()
        public_key = private_key.publicKey()
        private_key, public_key = (private_key.toPem(), public_key.toPem())
    elif config.DIGITAL_SIGNATURE_ALGO=='SCHNORR':
        '''
        We guess some private keys that satisfies certain properties.. ie. it's on the curve
        '''
        trying = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
        n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
        trying_byte = trying.to_bytes(32, byteorder="big")
        n_byte = n.to_bytes(32, byteorder="big") # convert msg to BYTE
        
        trying_int = schnorr.int_from_bytes(trying_byte)
        n_int = schnorr.int_from_bytes(n_byte)
        
        while( trying_int >= n_int-1) :
                    trying = os.urandom(32) # trying is bytes
                    trying_int = schnorr.int_from_bytes(trying) # convert bytes to integer
                    
        private_key = trying
        public_key = schnorr.pubkey_gen(private_key)
        public_key, private_key = (bytes_to_hex(public_key), bytes_to_hex(private_key))
    else: 
        log_error("[security.ppk_keygen.ppk_keygen] Unknown keygen algo defined")
        

    return public_key, private_key

def ppk_get_back_object(public_key=None,private_key=None):
    if config.DIGITAL_SIGNATURE_ALGO=='ECDSA':
        if private_key:
            private_key = PrivateKey.fromPem(private_key)
        if public_key:
            public_key = PublicKey.fromPem(public_key)
    elif config.DIGITAL_SIGNATURE_ALGO == 'SCHNORR':
        if private_key:
            private_key = hex_to_bytes(private_key)
        if public_key:
            public_key = hex_to_bytes(public_key)
    else:
        log_error("[security.ppk_keygen.ppk_get_back_object] Unknown keygen algo defined")
        
    return public_key, private_key