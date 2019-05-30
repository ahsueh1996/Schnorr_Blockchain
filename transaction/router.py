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
import json
from requests.exceptions import ConnectionError
app = Flask(__name__)

# Instantiate the Blockchain



transaction = Transaction()


@app.route('/')
def index():
	return render_template('./index.html')

@app.route('/hash')
def gettransactionID():
	response=transaction.gettransactionID('0100000001c997a5e56e104102fa209c6a852dd90660a20b2d9c352423edce25857fcd3704000000004847304402204e45e16932b8af514961a1d3a1a25fdf3f4f7732e9d624c6c61548ab5fb8cd410220181522ec8eca07de4860a4acdd12909d831cc56cbbac4622082221a8768d1d0901ffffffff0200ca9a3b00000000434104ae1a62fe09c5f51b13905f07f06b99a2f7159b2225f374cd378d71302fa28414e7aab37397f554a7df5f142c21c1b7303b8a0626f1baded5c72a704f7e6cd84cac00286bee0000000043410411db93e1dcdb8a016b49840f8c53bc1eb68a382e97b1482ecad7b148a6909a5cb2e0eaddfb84ccf9744464f82e160bfa9b8b64f9d4c03f999b8643f656b412a3ac00000000')
	return response





@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.form
    # Check that the required fields are in the POST'ed data
    required = ['sender_address', 'recipient_address', 'amount', 'signature']
    if not all(k in values for k in required):
        return 'Missing values', 400
    # Create a new Transaction
    
    transaction_result = transaction.submit_transaction(values['sender_address'], values['recipient_address'], values['amount'], values['signature'])
      
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
	
@app.route('/transactions/get', methods=['GET'])
def get_transactions():
    #Get transactions from transactions pool
    chaindata_dir = conf.TRANSACTION_DIR
    transactions  = []   
    array={}
    for i, filename in enumerate(sorted(os.listdir(chaindata_dir))):
        with open('%s%s' %(chaindata_dir, filename)) as file:
            transaction = json.load(file)
            
            array[filename]=transaction
            

    response =transactions
    return jsonify(array), 200	
	

@app.route('/sync/transaction', methods=['GET'])
def sync_transaction():
	# check file mình có 
    transaction_dir =conf.TRANSACTION_DIR
    arr={}
    for i, filename in enumerate(sorted(os.listdir(transaction_dir))):
        with open('%s%s' %(transaction_dir, filename)) as file:
            transaction = json.load(file)
            arr[filename] =transaction
    
    
    # check file node khác
    for node in conf.PEERS:
        url     =   node + "transactions/get"
        try:
            res     =   requests.get(url)
        except ConnectionError:
            print("connect false " +url)
            continue
        print('connect to '+url )
        
        data    =   res.json()
        for dict_key,dict_val in data.items():
            
            check = True
            if(len(arr)==0):
                check =False
            for mykey,myval in arr.items():
                if(dict_key != mykey and dict_val != myval):
                    check =False
                
            if(check== False):
                filename =transaction_dir + dict_key
                file = open(filename, 'w')
                file.write(json.dumps(dict_val, indent=4))
                file.close()
                print('sync success')



@app.route('/broadcast/transaction', methods=['GET'])
def broadcast_transaction():
    chaindata_dir = conf.TRANSACTION_DIR
   
            

    # check file node khác
    for node in conf.PEERS:
        url     =   node + "broadcast/save/transaction"
        print('connect host ' +node)
        try:

            for i, filename in enumerate(sorted(os.listdir(chaindata_dir))):
                with open('%s%s' %(chaindata_dir, filename)) as file:
                    transaction = json.load(file)
                    res     =   requests.post(url,json=transaction)
        except ConnectionError:
            print("connect false " +url)
            continue
        print('connect to '+url )
        

@app.route('/broadcast/save/transaction', methods=['POST'])
def broadcast_save_transaction():
    
    data=request.json
    data= to_dict(data)
    hash_data = dict_to_binary(data)
    file_name=sha256(hash_data.encode('utf-8'))



    transaction_dir =conf.TRANSACTION_DIR
    arr={}
    if len(os.listdir(transaction_dir) ) == 0:
        filename = transaction_dir + file_name
        file = open(filename, 'w')
        file.write(json.dumps(data, indent=4))
        file.close()
    else:    
        for i, filename in enumerate(sorted(os.listdir(transaction_dir))):
            with open('%s%s' %(transaction_dir, filename)) as file:
                transaction = json.load(file)
                if(file_name != filename):
                    print('broadcash success')
                    filename =transaction_dir + file_name
                    file = open(filename, 'w')
                    file.write(json.dumps(data, indent=4))
                    file.close()