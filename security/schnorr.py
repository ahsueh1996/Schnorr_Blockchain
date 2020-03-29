import hashlib
import binascii

p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F #32 bytes
#p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Points are tuples of X and Y coordinates and the point at infinity is
# represented by the None keyword.
G = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798, 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)

# This implementation can be sped up by storing the midstate after hashig
# tag_hash instead of rehashing it all the time.
def tagged_hash(tag, msg):
    tag_hash = hashlib.sha256(tag.encode()).digest()
    return hashlib.sha256(tag_hash + tag_hash + msg).digest()

def is_infinity(P):
    return P is None

def x(P):
    return P[0]

def y(P):
    return P[1]

def point_add(P1, P2):
    if (P1 is None):
        return P2
    if (P2 is None):
        return P1
    if (x(P1) == x(P2) and y(P1) != y(P2)):
        return None
    if (P1 == P2):
        lam = (3 * x(P1) * x(P1) * pow(2 * y(P1), p - 2, p)) % p
    else:
        lam = ((y(P2) - y(P1)) * pow(x(P2) - x(P1), p - 2, p)) % p
    x3 = (lam * lam - x(P1) - x(P2)) % p
    return (x3, (lam * (x(P1) - x3) - y(P1)) % p)

def point_mul(P, n):
    R = None
    for i in range(256):
        if ((n >> i) & 1):
            R = point_add(R, P)
        P = point_add(P, P)
    return R

def bytes_from_int(x):
    return x.to_bytes(32, byteorder="big")

def bytes_from_point(P):
    return bytes_from_int(x(P))

def point_from_bytes(b):
    x = int_from_bytes(b)
       
    if x >= p:
        print("#### x ", x)
        return None
    y_sq = (pow(x, 3, p) + 7) % p
    y = pow(y_sq, (p + 1) // 4, p)
    
    print("######################", y)
    print("######################", x)
    print("###################### ", (pow(y, 2, p) - pow(x, 3, p)) % p)
     
    if pow(y, 2, p) != y_sq:
        print("#### pow(y, 2, p) = ", pow(y, 2, p))
        print("#### y_sq = ", y_sq)
        return None
    return [x, y]

def int_from_bytes(b):
    return int.from_bytes(b, byteorder="big")

def hash_sha256(b):
    return hashlib.sha256(b).digest()

def is_square(x):
    return pow(x, (p - 1) // 2, p) == 1

def has_square_y(P):
    return not is_infinity(P) and is_square(y(P))

''' TO DO # DELETE '''
def pubkey_gen(seckey): 
    x = int_from_bytes(seckey)
    if not (1 <= x <= n - 1):
        raise ValueError('The secret key must be an integer in the range 1..n-1.')
    P = point_mul(G, x)
    return bytes_from_point(P)

def schnorr_sign(msg, seckey0):
    ''' ---------------------------------------------------------------------------------------- '''
#    msg = "5E2D58D8B3BCDF1ABADEC7829054F90DDA9805AAB56C77333024B9D0A508B75C"
    print("==== sent msg = ", msg)
    msg_hex = int("0x"+msg, 16) # convert msg to HEX
    msg_byte = msg_hex.to_bytes(32, byteorder="big") # convert msg to BYTE
    seckey0_hex=0xC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B14E5C9
    seckey0_byte = seckey0_hex.to_bytes(32, byteorder="big")  # convert msg to BYTE #3
    seckey0_byte_32=seckey0_byte
    print("########## seckey0_byte ########## ", seckey0_byte)
    print("########## seckey0_byte ########## ", seckey0_byte.hex())
    ''' ---------------------------------------------------------------------------------------- '''
    if len(msg_byte) != 32:
        raise ValueError('The message must be a 32-byte array.')
    seckey0 = int_from_bytes(seckey0_byte_32)
    if not (1 <= seckey0 <= n - 1):
        raise ValueError('The secret key must be an integer in the range 1..n-1.')
    P = point_mul(G, seckey0)
    seckey = seckey0 if has_square_y(P) else n - seckey0
    k0 = int_from_bytes(tagged_hash("BIPSchnorrDerive", bytes_from_int(seckey) + msg_byte)) % n
    if k0 == 0:
        raise RuntimeError('Failure. This happens only with negligible probability.')
    R = point_mul(G, k0)
    k = n - k0 if not has_square_y(R) else k0
    e = int_from_bytes(tagged_hash("BIPSchnorr", bytes_from_point(R) + bytes_from_point(P) + msg_byte)) % n
    return bytes_from_point(R) + bytes_from_int((k + e * seckey) % n)

def schnorr_verify(msg, pubkey, sig):
    ''' ---------------------------------------------------------------------------------------- '''
#    msg = "5E2D58D8B3BCDF1ABADEC7829054F90DDA9805AAB56C77333024B9D0A508B75C"
    print("==== received msg = ", msg)
    msg_hex = int("0x"+msg, 16) # convert msg to HEX
    msg_byte = msg_hex.to_bytes(32, byteorder="big") # convert msg to BYTE
    '''
    pubkey_hex = int("0x"+pubkey, 16) # convert pubkey to HEX
    pubkey_byte = pubkey_hex.to_bytes(608, byteorder="big")  # convert msg to BYTE #608
    
#    pubkey_byte_32 = pubkey_byte[0:32]
    pubkey_byte_32 = pubkey_byte[576:608] #576:608
    '''
 #   pubkey_hex=0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
 #   pubkey_hex=0xDFF1D77F2A671C5F36183726DB2341BE58FEAE1DA2DECED843240F7B502BA659
    pubkey_hex=0xDD308AFEC5777E13121FA72B9CC1B7CC0139715309B086C960E18FD969774EB8
    pubkey_byte = pubkey_hex.to_bytes(32, byteorder="big")  # convert msg to BYTE #3
    pubkey_byte_32=pubkey_byte
    
    print("===== pubkey_hex = ", hex(pubkey_hex))
    print("===== pubkey_byte = ",  pubkey_byte)
    print("===== pubkey_byte_32 = ",  pubkey_byte_32)
    
    sig_hex = int("0x"+sig, 16) # convert seckey to HEX
    sig_byte = sig_hex.to_bytes(64, byteorder="big") # convert msg to BYTE
    
    print("===== sig_byte = ", sig_byte)
    ''' ---------------------------------------------------------------------------------------- '''
    
    if len(msg_byte) != 32:
        raise ValueError('The message must be a 32-byte array.')
 #   if len(pubkey_byte_32) != 32:
 #       raise ValueError('The public key must be a 32-byte array.')
    if len(sig_byte) != 64:
        raise ValueError('The signature must be a 64-byte array.')
    P = point_from_bytes(pubkey_byte_32)
    if (P is None):
        print("---- HERE ----")
        return False
    r = int_from_bytes(sig_byte[0:32])
    s = int_from_bytes(sig_byte[32:64])
    ''' ---------------------------------------------------------------------------------------- '''
    print("======= r = ", r)
    print("======= s = ", s)
    print("======= n = ", n)
    ''' ---------------------------------------------------------------------------------------- '''
    if (r >= p or s >= n):
        return False
    print("%%%% ok")
    e = int_from_bytes(tagged_hash("BIPSchnorr", sig_byte[0:32] + pubkey_byte_32[0:32]  + msg_byte)) % n
    print("%%%% e = ", e)
    R = point_add(point_mul(G, s), point_mul(P, n - e))
    ''' ---------------------------------------------------------------------------------------- '''
    print("======= R = ", R)
    print("======= has_square_y(R) = ", has_square_y(R))
    ''' ---------------------------------------------------------------------------------------- '''
    if R is None or not has_square_y(R) or x(R) != r:
        return False
    return True


