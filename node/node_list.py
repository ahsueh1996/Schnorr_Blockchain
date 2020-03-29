# Native packages
import socket  

# Project packages
import utils
import config

class Node_Registry():
    def __init__(self):
        self.hostname = socket.gethostname()    
        self.ip = socket.gethostbyname(hostname) 
        self.nodemap = utils.map_csv(utils.read_file(config.NODE_CSV_FILE))
        self.id = nodemap[ip][1]
        self.peers = nodemap[ip][2]
    