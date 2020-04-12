# Native packages
import os
import sys
import math
import time
import json
import pickle
import requests
import collections
from itertools import islice
from flask import request
from requests.exceptions import ConnectionError

# Project packages
sys.path.append(".")
import config
# dynamic_log_level = config.Dynamic_Log_Level()


class Dynamic_Log_Level():
    class _singleton():
        def __init__(self, level):
            self.user_set_log_level = level
            self.dynamic_log_level = level
    
    singleton = None
            
    def __init__(self, level=None):
        if not self.singleton:
            self.singleton = Dynamic_Log_Level._singleton(level)
        elif self.singleton!=None and level!=None:
            self.singleton = Dynamic_Log_Level._singleton(level)
        
    def set_log_level(self, level):
        self.singleton.dynamic_log_level = level
    
    def reset_user_log_level(self):
        self.singleton.dynamic_log_level = self.singleton.user_set_log_level
        
        
    def get_dynamic_log_level(self):
        return self.singleton.dynamic_log_level
dynamic_log_level = Dynamic_Log_Level(config.LOG_LEVEL)

class Unbuffered:
    def __init__(self, stream, file=None):
    
        self.stream = stream
        if file:
            self.fstream = open(file,'w')  # File where you need to keep the logs
        else:
            self.fstream=None
    
    def write(self, data):
        self.stream.write(data)
        self.stream.flush()
        if self.fstream:
            self.fstream.write(data)    # Write the data of stdout here to a text file as well
   
    def flush(self):
        pass
# LOG_FILE = config.LOG_FILE
# # sys.stdout=Unbuffered(sys.stdout, LOG_FILE)

def progress(cur,total,description):
    return
    if dynamic_log_level.get_dynamic_log_level() >= config.VERBOSE:
        sys.stdout.write("\r\t[{}/{}]\t{}".format(cur,total,description))
        if cur == total:
            sys.stdout.write("\n")
        sys.stdout.flush()
    
def log_error(msg,args=[]):
    msg = "\t[ERROR] " + msg
    if dynamic_log_level.get_dynamic_log_level() >= config.QUIET:
        raise ValueError(msg,args)
    else:
        print(msg)
        
def log_warn(msg):
    if dynamic_log_level.get_dynamic_log_level() >= config.WARN:
        print("\t[WARN] " + msg)

def log_info(msg):
    if dynamic_log_level.get_dynamic_log_level() >= config.VERBOSE:
        print("\t[INFO] " + msg)
        
        
def save_pickle(serializable_data, file_dir):
    f = open(file_dir,'wb')
    pickle.dump(serializable_data,f)
    f.close()
    
def load_pickle(file_dir):
    f = open(file_dir, 'rb')
    ret = pickle.load(f, encoding='latin-1')
    f.close()
    return ret

def time_millis():
    return int(round(time.time() * 1000))

def format_dict_to_str(d):
    return json.dumps(d, indent = 4)

class ListDict:
    '''
    ld = ListDict()        
    ld.append('hi',1)
    ld.append('by',2)
    ld.append('cii',3)
    ld.append('hii',4)
    ld.append('byy',5)
    ld.append('ci',6)
    print(ld[0:6:2])
    print(ld[4:0:2])
    print(ld[[0,2,1]])
    print(ld[{'by'}])
    for each in ld:
        print(each)
    print (1 in ld)
    print ('by' in ld)
    ld.delete({'by'})
    '''
    def __init__(self,d={}):
        self.dict = collections.OrderedDict(d)
        self._index = 0
        
    def __getitem__(self,key_or_ind):
        if len(self) == 0:
            raise IndexError
        ttype, sel = self.recover_key_or_ind(key_or_ind)
        if ttype == 'key':
            return self.dict[sel]
        elif ttype == 'ind':
            ret = []
            for ind in sel:
                kv = next(islice(self.dict.items(), ind, None))
                ret.append(kv[1])
            return ret
        elif ttype == 'int':
            return next(islice(self.dict.items(), sel, None))[1]
        
    def __next__(self):
        if self._index >= len(self):
            self._index=0
            raise StopIteration
        else:
            ret = self[[self._index]]
            self._index +=1
        return ret
    
    def __len__(self):
        return len(self.dict)
    
    def contains_key(self, key):
        return key in self.dict
    
    def delete(self,key_or_ind):
        ttype, sel = self.recover_key_or_ind(key_or_ind)
        if ttype == 'key':
            del(self.dict[sel])
        elif ttype == 'ind':
            sel_key = []
            for ind in sel:
                sel_key.append(next(islice(self.dict.items(), ind, None))[0])
            for key in sel_key:
                del(self.dict[key])
    
    def recover_key_or_ind(self, key_or_ind):
        ret = [None, None]
        if type(key_or_ind) == int:
            '''understand this as index... for each in and such uses this'''
            return 'int', key_or_ind
        if type(key_or_ind) == set:
            ''' we can't accept multiple items in the set since set is unordered'''
            return 'key', list(key_or_ind)[0]
        if type(key_or_ind) == list:
            ret = [ 'ind', key_or_ind]
        if type(key_or_ind) == slice:
            r = key_or_ind.indices(len(self)-1)
            if r[1] == r[0]:
                ret = ['ind', [r[0]]]
            else:
                step_sign = (r[1]-r[0])//abs(r[1]-r[0])
                step_mag = abs(r[2])
                step = step_mag * step_sign
                ret = [ 'ind', [r[0]+step*i for i in range(math.ceil((abs(r[1]-r[0])+1)/step_mag))]]
        if ret[0] == 'ind':
            ret[1] = [ind%len(self) if ind < 0 else ind for ind in ret[1]]
            return ret[0], ret[1]
    
    def append(self, key, value):
        self.dict.update({key:value})   

    
    

def broadcast(serializable_data, peers, route):
    '''
    Use this function with @app.route method=['POST'] functions
    '''
    data = json.dumps(serializable_data)
    failed = 0
    for i, peer in enumerate(peers):
        peer_broadcast_url = config.CONNECTION_ADAPTER + peer + route
        progress(i, len(peers), "[utils.broadcast] Post req @ {}".format(peer_broadcast_url))
        try:
            r = requests.post(peer_broadcast_url, data=data)
            progress(i, len(peers), "[utils.broadcast] Post received, reply: ".format(r.content))
        except (ConnectionError, requests.exceptions.InvalidSchema, requests.exceptions.InvalidURL) as e:
            log_warn("[utils.broadcast] Post failed")
            failed = failed + 1
    if failed > 0:
        progress(len(peers), len(peers), "[utils.broadcast] Broadcast incomplete (failed)/(total): {}/{}".format(failed,len(peers)))
    else:
        progress(len(peers), len(peers), "[utils.broadcast] Broadcast complete    ")
        
        
def receive(serialized_data):
    '''
    Use this function with @app.route method=['POST'] functions
    '''
    # serialized_data = flask.request.data CALL THIS AT THE POSTED FUNCTION
    data = json.loads(serialized_data)
    log_info('[utils.receive] received data of type {}'.format(str(type(data))))
    return data


def read_file(filename):
    '''
    Takes a filename (absolute path to file) and returns a list
    of strings where each item in the list is the line in file f.
    '''
    f = open(filename, "r")
    lines = []
    for line in f:
        lines.append(line)
    return lines

'''
Immediately after read_file, you can pass the list of lines in this function
to get a matrix of strings representing the original file. \n are stripped.
'''
def split_line(line):
    return line.strip('\n').split(',')

def split_lines(lines):
    return [split_line(line) for line in lines]

def map_csv(lines):
    '''
    This function can also be called immediately after READ_CSV. It will return a
    map from col 0 to col 1 by interpreting col 0 and 1 according to the user specification
    '''
    m = split_lines(lines)
    my_map = {}
    for row in m:
        if len(row) >= 2:
            my_map[row[0]] = row
    return my_map