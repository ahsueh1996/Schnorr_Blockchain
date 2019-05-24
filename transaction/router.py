from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from transaction import Transaction
from wallet import Wallet

import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import requests
import config as conf
from tools import *

app = Flask(__name__)

# Instantiate the Blockchain



transaction = Transaction()


@app.route('/')
def index():
	return render_template('./index.html')

@app.route('/hash')
def gettransactionID(rawhax):
	response=transaction.gettransactionID('01000000017967a5185e907a25225574544c31f7b059c1a191d65b53dcc1554d339c4f9efc010000006a47304402206a2eb16b7b92051d0fa38c133e67684ed064effada1d7f925c842da401d4f22702201f196b10e6e4b4a9fff948e5c5d71ec5da53e90529c8dbd122bff2b1d21dc8a90121039b7bcd0824b9a9164f7ba098408e63e5b7e3cf90835cceb19868f54f8961a825ffffffff014baf2100000000001976a914db4d1141d0048b1ed15839d0b7a4c488cd368b0e88ac00000000')
	return jsonify(response), 201





@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.form
    # Check that the required fields are in the POST'ed data
    required = ['sender_address', 'recipient_address', 'amount', 'signature']
    if not all(k in values for k in required):
        return 'Missing values', 400
    # Create a new Transaction
    
    transaction_result = transaction.submit_transaction(values['sender_address'], values['recipient_address'], values['amount'], values['signature'])
    return jsonify(transaction_result)

    if transaction_result == False:
        response = {'message': 'Invalid Transaction!'}
        return jsonify(response), 406
    else:

        response = {'message': 'Transaction will be added to Block '+ str(transaction_result)}
        return jsonify(response), 201












@app.route('/make/transaction')
def make_transaction():
    return render_template('./make_transaction.html')

@app.route('/view/transactions')
def view_transaction():
    return render_template('./view_transactions.html')

@app.route('/wallet/new', methods=['GET'])
def new_wallet():
	random_gen = Crypto.Random.new().read
	private_key = RSA.generate(1024, random_gen)
	public_key = private_key.publickey()

	private_key = binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii')
	public_key = binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii')



	address 	= create_address(public_key)
	response = {
		'private_key': 	private_key,
		'public_key': 	public_key,
		'address'	:	address
	}
	array={}
	array['private_key']=private_key
	array['public_key']=public_key

	array['address']=address
	array['timestamp']=strftime("%Y-%m-%d %H:%M:%S", gmtime())

	wallet = Wallet(array)
	wallet.save_wallet()


	return jsonify(response), 200

@app.route('/generate/transaction', methods=['POST'])
def generate_transaction():
	
	sender_address = request.form['sender_address']
	sender_private_key = request.form['sender_private_key']
	recipient_address = request.form['recipient_address']
	value = request.form['amount']

	transaction = Transaction(sender_address, sender_private_key, recipient_address, value)

	
	array={}
	array['address']=sender_address
	array['public_key']=''
	array['private_key']=sender_private_key
	array['timestamp']=1
	check_wallet_out= Wallet(array)
	check_wallet_out=check_wallet_out.ischeck_address()

	array['address']=recipient_address
	check_wallet_in= Wallet(array)
	check_wallet_in=check_wallet_in.ischeck_address()
	try:
		response = {'transaction': transaction.to_dict(), 'signature': transaction.sign_transaction()}
		if(check_wallet_out and check_wallet_in ):
			return jsonify(response), 200
		else:
			return "Not address or private key" ,500
	except:
		return "Not address or private key" ,500
	
		
