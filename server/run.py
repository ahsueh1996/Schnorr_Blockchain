from argparse import ArgumentParser
from router import app
from blockchain import blockchain
from threading import Thread
from sync import *

def run_blockchain():
    sync_overall()
    blockchain.start()

if __name__ == '__main__':
    Thread(target=run_blockchain).start()
    
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    app.run(host='127.0.0.1', port=port)
