from argparse import ArgumentParser
from router import app
from blockchain import blockchain
from threading import Thread
from sync import sync
import mine
import apscheduler
from config import *

def run_blockchain():
    sync.sync_overall()

if __name__ == '__main__':
    sync.sync_overall()
    
    from apscheduler.schedulers.background import BackgroundScheduler
    sched = BackgroundScheduler(standalone=True)
    
    mine.sched = sched
    sched.add_job(mine.mine_for_block, kwargs={
                  'rounds': STANDARD_ROUNDS, 'start_nonce': 0}, id='mining')  # add the block again
    sched.add_listener(mine.mine_for_block_listener,
                       apscheduler.events.EVENT_JOB_EXECUTED)  # , args=sched)
    sched.start()
    
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    app.run(host='127.0.0.1', port=port)
