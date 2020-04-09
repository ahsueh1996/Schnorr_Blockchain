# Native packages
import sys
import signal
import requests
import apscheduler
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler

# Project packages
sys.path.append('.')
from node.blockchain import Blockchain
from node.node_list import Node_Registry
from node.scheduled_routines import SCHED_validate_and_add_possible_block
from utils import log_info, log_warn, log_error, progress


# Instantiate the Node
app = Flask(__name__)
CORS(app)
node_resistry = Node_Registry()
blockchain = Blockchain(node_resistry.id, node_resistry.peers)
sched = BackgroundScheduler(standalone=True)

def EXIT(signal, frame):
    log_warn("\n\n------EXITING------")
    try:
            sched.remove_job('mining')
            log_warn('Removed "mining" job')
    except apscheduler.jobstores.base.JobLookupError:
            log_warn('No "mining" job found')
    try:
        sched.shutdown()
        log_warn("sched shutdown (ok)")
    except apscheduler.schedulers.SchedulerNotRunningError:
        log_warn("sched shutdown (not ok)")
        pass
    log_warn("sys exit now...")
    sys.exit(0)

@app.route('/')
def index():
    return 'root'

@app.route('/peer_gossiped_new_block', methods=['POST'])
def import_block_from_other_node():
    mine.sched.add_job(SCHED_validate_and_add_possible_block, args=[new_block_dict], id='validate_possible_block')
    return "blockchain_{}_received_block".format(blockchain.chain_id)


@app.route('/peer_gossiped_new_transaction', methods=['POST'])
def import_transaction_from_other_node():
    mine.sched.add_job(SCHED_validate_and_add_possible_transaction, args=[new_block_dict], id='validate_possible_transaction')
    return "blockchain_{}_received_transaction".format(blockchain.chain_id)

