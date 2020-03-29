# Native packages
import os
import sys
import math
import time
import pickle
import collections
from itertools import islice
from requests.exceptions import ConnectionError

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

def time_millis():
    return int(round(time.time() * 1000))

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
        ttype, sel = self.recover_key_or_ind(key_or_ind)
        if ttype == 'key':
            return self.dict[sel]
        elif ttype == 'ind':
            ret = []
            for ind in sel:
                ret.append(self.dict[next(islice(self.dict.items(), ind, None))[0]])
            return ret
        elif ttype == 'int':
            return next(islice(self.dict.items(), sel, None))
        
    def __next__(self):
        if self._index >= len(self):
            self._index=0
            raise StopIteration
        else:
            ret = self[[self._index]][0]
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
    data = pickle.dumps(serializable_data)
    for i, peer in enumerate(peers):
        peer_broadcast_url = peer + route
        progress(i, len(peers), "Post req @ {}".format(peer_broadcast_url))
        try:
            r = requests.post(peer_broadcast_url, data=data)
            progress(i, len(peers), "Post received, reply: ".format(r.content))
        except ConnectionError:
            progress(i, len(peers), "Post failed")
    progress(len(peers), len(peers), "Broadcast to route, completed: {}".format(route))


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