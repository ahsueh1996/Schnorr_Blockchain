import os

ROOT_DIR = os.getcwd()

DIGITAL_SIGNATURE_ALGO = 'ECDSA'
HASH_ALGO = 'SHA256'

IGNORE = 0
QUIET = 1
WARN = 2
VERBOSE = 3
LOG_LEVEL = 3
LOG_FILE = "./log.txt"


MINING_REWARD = 1
MINING_DIFFICULTY = 6

BLOCK_LIMIT = 10
TRANSACTION_RATE = 3 # TRANS_RATE x (nodes in network) / (avg mining time) = load per unit time that the network is dealing with
NOUNCE_DISTANCE = 50000

NODE_CSV_FILE = "./node/node_list.csv"

CONNECTION_ADAPTER = "http://"

MASTER="155.138.145.252:5000"
END_OF_CHAIN = 15



    
    
