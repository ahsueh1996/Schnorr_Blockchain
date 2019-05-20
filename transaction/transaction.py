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

    # def create_address(self, publickey):
        # return ripemd160(SHA(publickey))

    def submit_transaction(self, sender_address, recipient_address, value, signature):
            """
            Add a transaction to transactions array if the signature verified
            """

            transaction = OrderedDict({'sender_address': sender_address, 
                                        'recipient_address': recipient_address,
                                        'value': value})
            transaction1 = OrderedDict(
                                        {
                                            "locktime": '0',# 4 bytes   Set a minimum block height or Unix time that this transaction can be included in.
                                            "txid": "c1b4e695098210a31fe02abffe9005cffc051bbe86ff33e173155bcbdc5821e3",
                                            "hash": "c1b4e695098210a31fe02abffe9005cffc051bbe86ff33e173155bcbdc5821e3",
                                            "version": len(self.transactions),
                                            "size": 191,
                                            "vsize": 191,
                                            "weight": 764,
                                            'input_count':1,
                                            'input':OrderedDict({
                                                "txid": "fc9e4f9c334d55c1dc535bd691a1c159b0f7314c54745522257a905e18a56779",# 32 bytes	Refer to an existing transaction.
                                                "vout": 1,# 4 bytes	Select one of its outputs.
                                                "scriptSig": {
                                                    "asm": "304402206a2eb16b7b92051d0fa38c133e67684ed064effada1d7f925c842da401d4f22702201f196b10e6e4b4a9fff948e5c5d71ec5da53e90529c8dbd122bff2b1d21dc8a9[ALL] 039b7bcd0824b9a9164f7ba098408e63e5b7e3cf90835cceb19868f54f8961a825",
                                                    "hex": "47304402206a2eb16b7b92051d0fa38c133e67684ed064effada1d7f925c842da401d4f22702201f196b10e6e4b4a9fff948e5c5d71ec5da53e90529c8dbd122bff2b1d21dc8a90121039b7bcd0824b9a9164f7ba098408e63e5b7e3cf90835cceb19868f54f8961a825"
                                                },  # A script that unlocks the input.                          
                                                'Sequence': signature # 4 bytes	
                                            }),
                                            'output_count':1,
                                            'output':OrderedDict({
                                                "value": float(value) /10**8 ,# 8 bytes	The value of the output in satoshis
                                                "n": 0,
                                                "scriptPubKey": {
                                                    "asm": "OP_DUP OP_HASH160 db4d1141d0048b1ed15839d0b7a4c488cd368b0e OP_EQUALVERIFY OP_CHECKSIG",
                                                    "hex": "76a914db4d1141d0048b1ed15839d0b7a4c488cd368b0e88ac",
                                                    "reqSigs": 1,
                                                    "type": "pubkeyhash",
                                                    "addresses": [
                                                        "1LzZJkQfz9ahY2SfetBHLcwyWmQRE9CwfU"
                                                    ]
                                                }#           A script that locks the output.
                                            }),
                                            
                                        }
                                    )
            #Reward for mining a block
            if sender_address == conf.MINING_SENDER:
                self.transactions.append(transaction)
                return len(self.chain) + 1
            #Manages transactions from wallet to another wallet
            else:
                transaction_verification = self.verify_transaction_signature(sender_address, signature, transaction)

                if transaction_verification:
                    self.transactions.append(transaction1)
                    return len(self.chain) + 1
                else:
                    return False



