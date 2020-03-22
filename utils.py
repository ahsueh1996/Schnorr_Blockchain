# Native packages
import os
import sys
import pickle
import collections
from itertools import islice

# Project packages
sys.path.append(".")
import config
LOG_LEVEL = config.LOG_LEVEL

def progress(cur,total,description):
    if LOG_LEVEL >= config.VERBOSE:
        sys.stdout.write("\r[{}/{}]\t{}".format(cur,total,description))
        if cur == total:
            sys.stdout.write("\n")
        sys.stdout.flush()
    
def log_error(msg,args=[]):
    msg = "[ERROR] " + msg
    if LOG_LEVEL >= config.QUIET:
        raise ValueError(msg,args)
    else:
        print(msg)
        
def log_warn(msg):
    if LOG_LEVEL >= config.WARN:
        print("[WARN] " + msg)

def log_info(msg):
    if LOG_LEVEL >= config.VERBOSE:
        print("[INFO] " + msg)
        
        
def save_pickle(serializable_data, file_dir):
    f = open(file_dir,'wb')
    pickle.dump(serializable_data,f)
    f.close()
    
def load_pickle(file_dir):
    f = open(file_dir, 'rb')
    ret = pickle.load(f, encoding='latin-1')
    f.close()
    return ret

class ListDict:
    def __init__(self,d={}):
        self.dict = collections.OrderedDict(d)
        
    def __getitem__(self,i):
        if i < 0 and abs(i) <= len(self):
            i = i % len(self)
        return self.dict[next(islice(self.dict.items(), i, None))[0]]
    
    def __len__(self):
        return len(self.dict)
    
    def append(self, key, value):
        self.dict.update({key:vlaue})        
    
    