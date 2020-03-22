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
    log_error("Unknown hash algo config -- returning 0")
    return 0


def dict_to_utf8 (d):
    return str(d).encoding('utf-8')