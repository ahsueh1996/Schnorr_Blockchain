import struct
import config as conf
import hashlib
import binascii
import struct
import sys
from binascii import hexlify, unhexlify
import base58
from time import gmtime, strftime
import json
import glob
import os
b58_digits = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


def RIPEMD160(string):
	string = binascii.a2b_hex(string)
	h = hashlib.new('ripemd160')
	h.update(string)
	return h.hexdigest()

def SHA256(string):
	string = binascii.a2b_hex(string)
	return hashlib.sha256(string).hexdigest()
def sha256(string):
	return hashlib.sha256(string).hexdigest()
def create_address(string):
	
	sha256		= SHA256(string)
	ripemd160	= RIPEMD160(sha256)
	add00		= "00"+ripemd160

	sha256		=SHA256(add00)

	sha256		=SHA256(sha256)

	string		=add00 + sha256[:8]
	string = binascii.a2b_hex(string)


	return base58.b58encode(string).decode("utf-8")		

def encrypt_string(hash_string):
    #binary
    string = binascii.a2b_hex(hash_string)
    #sha256
    sha_signature = hashlib.sha256(string).hexdigest()
    
    return sha_signature
def SwapEndian(string):
    ba = bytearray.fromhex(string)
    ba.reverse()
    s = ''.join(format(x, '02x') for x in ba)
    return s.upper()
    
def uint1(stream):
	return ord(stream.read(1))

def uint2(stream):
	return struct.unpack('H', stream.read(2))[0]

def uint4(stream):
	return struct.unpack('I', stream.read(4))[0]

def uint8(stream):
	return struct.unpack('Q', stream.read(8))[0]

def hash32(stream):
	return stream.read(32)[::-1]

def time(stream):
	time = uint4(stream)
	return time

def varint(stream):
	size = uint1(stream)

	if size < 0xfd:
		return size
	if size == 0xfd:
		return uint2(stream)
	if size == 0xfe:
		return uint4(stream)
	if size == 0xff:
		return uint8(stream)
	return -1

def hashStr(bytebuffer):
	return ''.join(('%02x'%ord(a)) for a in bytebuffer)



def dict_to_binary(the_dict):
    str = json.dumps(the_dict)
    binary = ' '.join(format(ord(letter), 'b') for letter in str)
    return binary


def binary_to_dict(the_binary):
    jsn = ''.join(chr(int(x, 2)) for x in the_binary.split())
    d = json.loads(jsn)  
    return d
#wallet
def get_wallet_from_address(address):
    with open(conf.WALLET_DIR + address+'.json') as file:
        wallet = json.load(file)
        return wallet
        file.close()
	

	