# Native packages
import socket  

# Project packages
import utils
import config

class Node_Registry():
    class _singleton():
        def __init__(self, port):
            self.hostname = socket.gethostname()    
            self.ip = socket.gethostbyname(self.hostname) 
            self.nodemap = utils.map_csv(utils.read_file(config.NODE_CSV_FILE))
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
    
    def __init__(self, port=None):
        if not self.singleton:
            self.singleton = Node_Registry._singleton(port)
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