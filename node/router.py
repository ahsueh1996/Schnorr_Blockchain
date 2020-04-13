# Native packages
import sys
import json
import signal
import random
import requests
import apscheduler
from flask import Flask, jsonify, request, render_template, request
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler

# Project packages
sys.path.append('.')
import utils
from node.blockchain import Blockchain
from node.node_list import Node_Registry
from node.scheduled_routines import SCHED_validate_and_add_possible_block, SCHED_validate_and_add_possible_transaction, SCHED_master_node
from utils import log_info, log_warn, log_error, progress


# Instantiate the Node
app = Flask(__name__)
CORS(app)
node_registry = Node_Registry()
blockchain = Blockchain(node_registry.id, node_registry.peers)
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
    random_id = random.randint(0,5000)
    log_info('[router./peer_gossiped_new_block]({}) Import block from another node...'.format(random_id))
    new_block_dict = utils.receive(request.data)
    log_info("[router./peer_gossiped_new_block]({}) Recieved block: {}".format(random_id,new_block_dict['block_hash'][:25]))
    sched.add_job(SCHED_validate_and_add_possible_block, args=[new_block_dict, blockchain, sched, random_id], id='validate_possible_block')
    log_info('[router./peer_gossiped_new_block]({}) Queued.'.format(random_id))
    return "blockchain_{}_received_block".format(blockchain.chain_id)


@app.route('/peer_gossiped_new_transaction', methods=['POST'])
def import_transaction_from_other_node():
    random_id = random.randint(0,5000)
    log_info('[router./peer_gossiped_new_transaction]({}) Import transaction from another node...'.format(random_id))
    new_transaction_dict = utils.receive(request.data)
    log_info("[router./peer_gossiped_new_transaction]({}) Recieved transaction: {}".format(random_id,new_transaction_dict['signature'][:25]))
    sched.add_job(SCHED_validate_and_add_possible_transaction, args=[new_transaction_dict, blockchain, random_id], id='validate_possible_transaction-'+str(random_id))
    log_info('[router./peer_gossiped_new_transaction]({}) Queued.'.format(random_id))
    return "blockchain_{}_received_transaction".format(blockchain.chain_id)

@app.route('/node_finished', methods=['POST'])
def node_finished():
    who = utils.receive(request.data)
    blockchain.peers.append(who)
    sched.add_job(SCHED_master_node, args=[blockchain, sched, node_registry], id='master_node')
    return "Ok master received. Thank you node."
    
@app.route('/sync_next_block', methods=['POST'])
def post_next_block():
    random_id = random.randint(0,5000)
    idx = int(utils.receive(request.data))
    log_info('[router./sync_next_block]({}) Posting block ({}) for requester...'.format(random_id, idx))
    block_list = blockchain.chain[[idx]]
    if len(block_list) !=0:
        block_list[0].export_block_to_dict()
    return json.dumps(block_dict)
    
    
def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/flask_shutdown', methods=['POST'])
def flask_shutdown():
    shutdown_server()
    return 'Flask Server shutting down...'