# Native package
import sys
import Crypto
import binascii
from ellipticcurve.ecdsa import Ecdsa
from ellipticcurve.signature import Signature
from hashlib import sha256

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

# Project package
sys.path.append('.')
import config
from utils import *
from security.hash import dict_to_hash, dict_to_byte_hash, dict_to_bytes, bytes_to_hex, hex_to_bytes
from security.schnorr import schnorr_sign, schnorr_verify
from security.ppk_keygen import ppk_get_back_object


def sign(dictionary_msg, sender_private_key):

    _, sk = ppk_get_back_object(private_key=sender_private_key)
        
    if config.DIGITAL_SIGNATURE_ALGO == 'ECDSA':
        h = str(dictionary_msg)
        signature = Ecdsa.sign(h, sk).toPem()
        log_info("[security.digital_signature.sign] ECDSA Signature: {}".format(signature))
        return signature
    
    elif config.DIGITAL_SIGNATURE_ALGO == 'SCHNORR':
        h = dict_to_hash(dictionary_msg)
        signature = schnorr_sign(h, sk)
        log_info("[security.digital_signature.sign] Schnorr Signature: {}".format(signature))
        return signature
    else:
        log_error("[security.digital_signature.sign] Unkown DSA in config -- cannot create digital signature!")




def verify(dictionary_msg, signature, sender_public_key):
    
    vk, _ = ppk_get_back_object(public_key=sender_public_key)
    if config.DIGITAL_SIGNATURE_ALGO == 'ECDSA':
        h = str(dictionary_msg)
        check = Ecdsa.verify(h, Signature.fromPem(signature), vk) # True
        log_info("[security.digital_signature.verify] ECDSA Verify result: {}".format(check))
        return check
    elif config.DIGITAL_SIGNATURE_ALGO == 'SCHNORR': 
        h = dict_to_hash(dictionary_msg)
        check = schnorr_verify(h, vk, signature)
        log_info("[security.digital_signature.verify] Schnorr Verify result: {}".format(check))
        return check
    else:
        log_error("[security.digital_signature.verify] Unknown DSA in config -- cannot verify signature!")