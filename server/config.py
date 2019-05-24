
MINING_SENDER = "THE BLOCKCHAIN"
MINING_REWARD = 1
MINING_DIFFICULTY = 6
CHAINDATA_DIR = 'chaindata/'
BROADCASTED_BLOCK_DIR = CHAINDATA_DIR + 'broadcasted_blocks'
BLOCK_VAR_CONVERSIONS = {'index', 'timestamp',
                         'previous_hash', 'transactions', 'diff'}



#WALLET
WALLET_DIR = 'wallet/'
WALLET_VAR_CONVERSIONS = {'private_key', 'public_key',
                         'address', 'timestamp'}

#Transaction
TRANSACTION_DIR = 'transaction_wait/'
TRANSACTION_VAR_CONVERSIONS = {'sender_address', 'recipient_address',
                         'value', 'timestamp'}                         