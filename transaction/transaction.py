'''
title           : blockchain_client.py
description     : A blockchain client implemenation, with the following features
                  - Wallets generation using Public/Private key encryption (based on RSA algorithm)
                  - Generation of transactions with RSA encryption      
author          : Adil Moujahid
date_created    : 20180212
date_modified   : 20180309
version         : 0.3
usage           : python blockchain_client.py
                  python blockchain_client.py -p 8080
                  python blockchain_client.py --port 8080
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


class Transaction:

    def __init__(self, sender_address="", sender_private_key="", recipient_address="", value=""):
        self.sender_address = sender_address
        self.sender_private_key = sender_private_key
        self.recipient_address = recipient_address
        self.value = value
        self.transactions = []
        self.chain = []

    def __getattr__(self, attr):
        return self.data[attr]

    def to_dict(self):
        return OrderedDict({'sender_address': self.sender_address,
                            'recipient_address': self.recipient_address,
                            'value': self.value})
    def verify_transaction_signature(self, sender_address, signature, transaction):
        """
        Check that the provided signature corresponds to transaction
        signed by the public key (sender_address)
        """
        public_key = RSA.importKey(binascii.unhexlify(sender_address))
        verifier = PKCS1_v1_5.new(public_key)
        h = SHA.new(str(transaction).encode('utf8'))
        return verifier.verify(h, binascii.unhexlify(signature))
    def sign_transaction(self):
        """
        Sign transaction with private key
        """
        private_key = RSA.importKey(binascii.unhexlify(self.sender_private_key))
        signer = PKCS1_v1_5.new(private_key)
        h = SHA.new(str(self.to_dict()).encode('utf8'))
        return binascii.hexlify(signer.sign(h)).decode('ascii')


    def submit_transaction(self, sender_address, recipient_address, value, signature):
            """
            Add a transaction to transactions array if the signature verified
            """

            transaction = OrderedDict({'sender_address': sender_address, 
                                        'recipient_address': recipient_address,
                                        'value': value})
            #Reward for mining a block
            if sender_address == conf.MINING_SENDER:
                self.transactions.append(transaction)
                return len(self.chain) + 1
            #Manages transactions from wallet to another wallet
            else:
                transaction_verification = self.verify_transaction_signature(sender_address, signature, transaction)

                if transaction_verification:
                    self.transactions.append(transaction)
                    return self.transactions
                    return len(self.chain) + 1
                else:
                    return False



