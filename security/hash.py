# Native package
import sys
import Crypto
import binascii
import hashlib

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

# Project package
sys.path.append('.')
import config
from utils import *


def data_hash(data):
    if config.HASH_ALGO == 'SHA256':
        sha = hashlib.sha256()
    if 'SHA' in config.HASH_ALGO:
        sha.update(data)
        return sha.hexdigest()
    log_error("[security.hash.data_hash] Unknown hash algo config -- returning None")
    return None


def dict_to_bytes (d):
    return str(d).encode('utf-8')

def hex_to_bytes(hex_string):
    return bytes.fromhex(hex_string)

def bytes_to_hex(bytes_):
    return bytes_.hex()


def dict_to_byte_hash(d):
    return hex_to_bytes(data_hash(dict_to_bytes(d)))

def dict_to_hash(d):
    return data_hash(dict_to_bytes(d))