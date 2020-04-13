## Native packages
import os
import sys
import socket
import random
from requests import get

# Project packages
sys.path.append('.')
import utils
import config

class Node_Registry():
    class _singleton():
        def __init__(self, port, file):
            self.hostname = socket.gethostname()    
            self.ip = get('https://api.ipify.org').text 
            self.nodemap = utils.map_csv(utils.read_file(file))
            self.port = ""
            self.id = 0
            self.peers = []
            if port:
                self.set_port_and_update(port)
            
        def set_port_and_update(self, port):
            self.port = ":" + str(port)
            self.update_id_and_peers()
        
        def update_id_and_peers(self):
            self.id = int(self.nodemap[self.ip+self.port][1])
            self.peers = self.nodemap[self.ip+self.port][2:]
        
        
    singleton = None
    
    def __init__(self, port=None, file=config.NODE_CSV_FILE):
        if not self.singleton:
            self.singleton = Node_Registry._singleton(port,file)
        self.update()
        
    def set_port_and_update(self,port):
        self.singleton.set_port_and_update(port)
        self.update()
    
    def update(self):
        self.ip = self.singleton.ip
        self.nodemap = self.singleton.nodemap
        self.port = self.singleton.port
        self.id = self.singleton.id
        self.peers = self.singleton.peers
        
    def generate_peers(self, num_peers):
        nodemap_keys = list(self.nodemap.keys())
        for i,key in enumerate(nodemap_keys):
            self.nodemap[key][1] = i
            rand_idx = [random.randint(0,len(nodemap_keys)-1) for j in range(num_peers+5)]
            self.nodemap[key][2] = []
            for k in rand_idx:
                if key == nodemap_keys[k]:
                    continue
                elif len(self.nodemap[key][2]) >= num_peers:
                    break
                else:
                    self.nodemap[key][2].append(nodemap_keys[k])
        
    def save_nodemap(self, csv_file):
        nodemap_keys = list(self.nodemap.keys())
        with open(csv_file,'w') as file:
            for i,key in enumerate(nodemap_keys):
                if i !=0:
                    file.write("\n")
                peers_string = str(self.nodemap[key][2]).replace('[','').replace(']','').replace("'","")
                output = "{},{},{}".format(key,self.nodemap[key][1],peers_string)
                file.write(output)       
        
                      
if __name__ == '__main__':
    """
    Given the following process_this.csv:
        127.0.0.1:5000,,
        192.168.2.0,,
        16.39.159.1,,
    and num_peers = 2 we obtain the follwoing process_this_output.csv:
        127.0.0.1:5000,0,192.168.2.0,16.39.159.1
        192.168.2.0,1,127.0.0.1:5000,16.39.159.1
        16.39.159.1,2,127.0.0.1:5000,192.168.2.0
    This is the expected input to Node_Registry when running the blockchain
    """
    csv_file = os.path.join(os.getcwd(),'node','process_this')
    num_peers = int(input('Number of peers: '))
    if num_peers == None:
        num_peers = 5
    nr = Node_Registry(None,csv_file+'.csv')
    nr.generate_peers(num_peers)
    nr.save_nodemap(csv_file+'_out.csv')
    print('Done')
    
    
                              