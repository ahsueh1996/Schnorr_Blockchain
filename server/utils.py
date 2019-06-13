from config import *
from block import Block
import datetime as date
import json
import os

def create_new_block_from_previous(previous_block=None):
    next_block = None
    if previous_block:  
        transactions = []
        transaction_dir = '../transaction/' + TRANSACTION_DIR
        for i, filename in enumerate(sorted(os.listdir(transaction_dir))):
            with open('%s%s' % (transaction_dir, filename)) as file:
                transaction = json.load(file)
                transactions.append(transaction)

        transactions = sorted(
            transactions, key=lambda x: x['value'], reverse=True)
        transactions = transactions[:5]

        # Mining block
        next_index = int(previous_block.index) + 1
        next_block = Block(
            index=str(next_index),
            timestamp=date.datetime.now(),
            transactions=transactions,
            previous_hash=previous_block.hash,
            diff=MINING_DIFFICULTY
        )
    else:
        next_block = Block(
            index=str(0),
            timestamp=date.datetime.now(),
            transactions=[],
            previous_hash="",
            diff=MINING_DIFFICULTY
        )
    return next_block
