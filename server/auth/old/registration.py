from collections import namedtuple
import struct

# from Crypto.PublicKey import RSA
# from Crypto.Random import get_random_bytes
# from Crypto.Hash import SHA256

from _defaults import *


# Public key contain and coud be made from two components:
# n - modulus   n = p * q
# e - exponent  e - random integer
Pb_key_parts = namedtuple('Pb_key_parts', ['n', 'e'])


def coroutine(func):
    def next_coro(*args, **kwargs):
        coro = func(*args, **kwargs)
        coro.__next__()
        return coro
    return next_coro


@coroutine
def process_registration(db_conn):
    client_pb_key_b = yield
    with db_conn:
	with db_conn.cursor() as curs:
	    curs.execute("INSERT INTO client(name, registration_time) VALUES(:
    print("In registration")

    yield


# client_pb_key = resolve_client_pb_key(client_pb_key_b)
# generate_server_key()
# priv_key = RSA.import_key(open("priv_key.bin").read(), passphrase=PASSPHRASE)
# pub_key = RSA.import_key(open("pub_key.bin").read())

# # Generate and encrypt secret sequence
# secret_seq = get_random_bytes(64)
# cipher_rsa = PKCS1_OAEP.new(client_pb_key)
# enc_secret_seq = cipher_rsa.encrypt(secret_seq)

# msg_len = pub_key.n.bite_size() + \
#           pub_key.e.bite_size()
# prepared_block = struct.pack(">I128s128s", msg_len, 
#                              pub_key.n, 
#                              pub_key.e)
# client_secret_seq_hash = resolve_secret_seq_hash(secret_seq_hash_b)
# if verify_client_hash(client_secret_seq_hash, secret_seq):
#     response = struct.pack(">Ic", STATUS_LEN, STATUS_SUCCESS)
#     with db_conn:
#         with db_conn.cursor() as cur:
#             cur.execute('')
# else:
#     response = struct.pack(">Ic", STATUS_LEN, STATUS_FAIL)

def resolve_client_pb_key(client_pb_key_b):
    pb_key_parts = Pb_key_parts()
    (pb_key_parts.n, pb_key_parts.e) = struct.unpack(">{0}s{1}s".format(MODULUS_LENGTH, E_LENGTH), client_pb_key_b)
    client_pb_key = RSA.construct((pb_key_parts.n, pb_key_parts.e))
    return client_pb_key


def resolve_secret_seq_hash(secret_seq_hash_b):
    secret_seq_hash = struct.unpack(">16s", secret_seq_hash_b)
    return secret_seq_hash


def verify_client_hash(client_hash, server_sequence):
    s_seq_hash = SHA256.new()
    s_seq_hash.update(b"{}".format(server_sequence))
    return client_hash == s_seq_hash.hexdigest()


def generate_server_key():
    key = RSA.generate(RSA_KEY_LENGTH)
    encrypted_key = key.export_key(passphrase=PASSPHRASE, pkcs=8,
                                   protection='scryptAndAES128-CBC')
    with open("priv_key.bin", 'w') as sp:
        sp.write(encrypted_key)
