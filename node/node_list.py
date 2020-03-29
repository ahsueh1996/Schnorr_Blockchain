# Native packages
import socket  

# Project packages
import utils
import config

class Node_Registry():
    def __init__(self):
        self.hostname = socket.gethostname()    
        self.ip = socket.gethostbyname(self.hostname) 
        nodemap = utils.map_csv(utils.read_file(config.NODE_CSV_FILE))
        self.id = int(nodemap[self.ip+":5000"][1])
        self.peers = nodemap[self.ip+":5000"][2:]
    