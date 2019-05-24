'''
title           : transaction.py
description     : A blockchain client implemenation, with the following features
                  - Wallets generation using Public/Private key encryption (based on RSA algorithm)
                  - Generation of transactions with RSA encryption      
author          : Adil Moujahid
date_created    : 20180212
date_modified   : 20180309
version         : 0.3
usage           : python run.py
                  python run.py -p 8080
                  python run.py --port 8080
python_version  : 3.6.1
Comments        : Wallet generation and transaction signature is based on [1]
References      : [1] https://github.com/julienr/ipynb_playground/blob/master/bitcoin/dumbcoin/dumbcoin.ipynb
'''

from collections import OrderedDict

import binascii
import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import requests
from flask import Flask, jsonify, request, render_template

import sys
sys.path.append('../server/')
import config as conf
import hashlib
import binascii
import struct
from tools import *
import json
import os
class Wallet:

    def __init__(self, wallet):
        self.private_key = wallet['private_key']
        self.public_key = wallet['public_key']
        self.address = wallet['address']
        self.timestamp=wallet['timestamp']
    def to_dict(self):
        return OrderedDict({'private_key': self.private_key,
                            'public_key': self.public_key,
                            'address': self.address,
                            'timestamp':self.timestamp
                            })

    def save_wallet(self):
        index_string = self.address

        filename = "{}{}.json".format(conf.WALLET_DIR,self.address) 

        print(" - New wallet saved to %s" % (filename))
        data = self.to_dict()
        file = open(filename, 'w')
        file.write(json.dumps(data, indent=4))
        file.close()
    def ischeck_address(self):
        exists = os.path.isfile(conf.WALLET_DIR + self.address+'.json')
        if exists:
            return True
            # Store configuration file values
        else:
            # Keep presets
            return False

