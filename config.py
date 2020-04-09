import os

ROOT_DIR = os.getcwd()

KEYGEN_ALGO = 'ECDSA'
DIGITAL_SIGNATURE_ALGO = 'ECDSA'
HASH_ALGO = 'SHA256'

IGNORE = 0
QUIET = 1
WARN = 2
VERBOSE = 3
LOG_LEVEL = 3
LOG_FILE = "./log.txt"


MINING_REWARD = 1
MINING_DIFFICULTY = 1

BLOCK_LIMIT = 10
NOUNCE_DISTANCE = 10000

NODE_CSV_FILE = "./node/node_list.csv"



class Dynamic_Log_Level():
    class _singleton():
        def __init__(self):
            self.user_set_log_level = LOG_LEVEL
            self.LOG_LEVEL = LOG_LEVEL
    
    singleton = None
            
    def __init__(self):
        if not self.singleton:
            self.singleton = Dynamic_Log_Level._singleton()
        
    def set_log_level(self, level):
        self.singleton.LOG_LEVEL = level
    
    def reset_user_log_level(self):
        self.singleton.LOG_LEVEL = self.singleton.user_set_log_level
        
        
    def get_dynamic_log_level(self):
        return self.singleton.LOG_LEVEL
    
