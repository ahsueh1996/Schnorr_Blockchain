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
from wallet import Wallet

class Transaction:

    def __init__(self, sender_address="", sender_private_key="", recipient_address="", value=""):
        self.sender_address = sender_address
        self.sender_private_key = sender_private_key
        self.recipient_address = recipient_address
        self.value = value
        self.transactions = []
        self.chain = []

        self.continueParsing = True
        self.magicNum = 0
        self.blocksize = 0
        self.blockheader = ''
        self.txCount = 0
        self.Txs = []


    def gettransactionID(self,rawhax):
        string	= rawhax
        hash1	=encrypt_string(string)
        hash2	=encrypt_string(hash1)
        transactionid	= SwapEndian(hash2)
        response = {'message': transactionid }
        return jsonify(response), 201

    def __getattr__(self, attr):
        return self.data[attr]

    def to_dict(self):
        return OrderedDict({'sender_address': self.sender_address,
                            'recipient_address': self.recipient_address,
                            'value': self.value})
    def to_dict2(self):
        wallet_sender = get_wallet_from_address(self.sender_address)
        wallet_recipient = get_wallet_from_address(self.recipient_address)


        return OrderedDict({'sender_address': wallet_sender['public_key'],
                            'recipient_address': wallet_recipient['public_key'],
                            'value': self.value})
    def verify_transaction_signature(self, sender_address, signature, transaction):
        """
        Check that the provided signature corresponds to transaction
        signed by the public key (sender_address)
        """
        sender_address =get_wallet_from_address(sender_address)['public_key']
        public_key = RSA.importKey(binascii.unhexlify(sender_address))
        verifier = PKCS1_v1_5.new(public_key)
        h = SHA.new(str(transaction).encode('utf8'))
        return verifier.verify(h, binascii.unhexlify(signature))
    def sign_transaction(self):
        """
        Sign transaction with private key
        """
        wallet = get_wallet_from_address(self.sender_address)
        private_key = RSA.importKey(binascii.unhexlify(wallet['private_key']))
        signer = PKCS1_v1_5.new(private_key)
        h = SHA.new(str(self.to_dict2()).encode('utf8'))
        return binascii.hexlify(signer.sign(h)).decode('ascii')

    # def create_address(self, publickey):
        # return ripemd160(SHA(publickey))

    def submit_transaction(self, sender_address, recipient_address, value, signature):
            """
            Add a transaction to transactions array if the signature verified
            """
            self.sender_address=sender_address
            self.recipient_address=recipient_address
            self.value=value

             
            transaction = OrderedDict({ 'sender_address': sender_address, 
                                        'recipient_address': recipient_address,
                                        'value': value,
                                        'timestamp':strftime("%Y-%m-%d %H:%M:%S", gmtime())
                                        })
            transaction_verification =self.to_dict2()


            transaction1 = OrderedDict(
                                        {
                                            "locktime": '0',# 4 bytes   Set a minimum block height or Unix time that this transaction can be included in.
                                            "txid": "c1b4e695098210a31fe02abffe9005cffc051bbe86ff33e173155bcbdc5821e3",
                                            "hash": "c1b4e695098210a31fe02abffe9005cffc051bbe86ff33e173155bcbdc5821e3",
                                            "version": len(self.transactions),
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

                transaction_verification = self.verify_transaction_signature(sender_address, signature, transaction_verification)

                if transaction_verification:
                    # path = conf.TRANSACTION_DIR
                    # file_list = os.listdir(path)
                    # list_of_files=sorted(file_list) 
                    # if(list_of_files):
                    #     latest_file = list_of_files[-1]
                    #     latest_file =latest_file.replace('.json', '')
                    #     latest_file = int(latest_file) +1
                    # else:
                    #     latest_file = 1
                    data = transaction
                    hash_data = dict_to_binary(data)
                    file_name=sha256(hash_data.encode('utf-8'))

                    filename = "{}{}.json".format(conf.TRANSACTION_DIR,file_name ) 

                    print(" - New wallet saved to %s" % (filename))
                    
                    file = open(filename, 'w')
                    file.write(json.dumps(data, indent=4))
                    file.close()

                    self.broadcast_transaction()
                    return len(self.chain) + 1
                else:
                    return False


    def broadcast_transaction(self):
        chaindata_dir = conf.TRANSACTION_DIR
    
            
        # check file node khác
        for node in conf.PEERS:
            url     =   node + "broadcast/save/transaction"
            print('connect host ' +node)
            try:

                for i, filename in enumerate(sorted(os.listdir(chaindata_dir))):
                    with open('%s%s' %(chaindata_dir, filename)) as file:
                        transaction = json.load(file)
                        res     =   requests.post(url,json=transaction)
            except ConnectionError:
                print("connect false " +url)
                continue
            print('connect to '+url )