'''
RUN FROM ROOT PACKAGE
'''

# Native packages
import os
import sys
import random
from argparse import ArgumentParser

# Project packages
sys.path.append('.')
import config
import utils
from utils import log_info, log_warn, log_error, progress
from security.ppk_keygen import ppk_keygen
from client.transaction import Transaction

#PARMETERS TO ABSTRACT OUT IN THE FUTURE
WALLETS_DIR = os.path.join(config.ROOT_DIR, 'client', 'wallets.pkl')
DEFAULT_NUM_WALLETS = 50

class Client:

    def __init__(self):
        self.wallets = []
        self.make_wallets(DEFAULT_NUM_WALLETS)
        self.load_wallets()
    
    @staticmethod
    def make_wallets(amount):
        data = []
        for i in range(amount):
            progress(i,amount-1,'making wallets...')
            pub, pri = ppk_keygen()
            wallet = {'public':pub,\
                      'private':pri}
            data.append(wallet)
        log_info('[client.Client.make_wallets] writing ({}) wallets to pickle...'.format(amount))
        utils.save_pickle(data,WALLETS_DIR)
    
    def load_wallets(self):
        # check if chaindata folder existed, create if not
        if not os.path.exists(WALLETS_DIR):
            Client.make_wallets(DEFAULT_NUM_WALLETS)
        self.wallets = utils.load_pickle(WALLETS_DIR)
        
    def generate_random_transaction(self):
        sender = random.randint(0,len(self.wallets)-1)      # apparently randint is inclusive..
        receiver = random.randint(0,len(self.wallets)-1)
        value = random.random()*1000
        transaction = Transaction(self.wallets[sender]['public'],self.wallets[sender]['private'],\
                                  self.wallets[receiver]['public'],value)
        transaction.sign_transaction()
        log_info("[client.Client.generate_random_transaction] transaction generated and signed: \n{}"\
                 .format(utils.format_dict_to_str(transaction.export_transaction_to_dict())))
        return transaction
    