from Crypto.Random import get_random_bytes
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA


def coroutine(func):
    def next_coro(*args, **kwargs):
        coro = func(*args, **kwargs)
        coro.__next__()
        return coro
    return next_coro


@coroutine
def process_login(db_conn):
    client_id_b = yield
    client_id = struct.unpack('L', client_id_b)[0]
    with db_conn:
        with db_conn.cursor() as cur:
            cur.execute("SELECT secret_seq FROM user WHERE user_id = %s", (str(client_id)))
            client_secret_seq = cur.fetchone()
    random_word = get_random_bytes(32)
    yield

    control_hash = yield random_word
    if not verify_control_hash(control_hash, random_word, client_secret_seq):
        response = b'0'
    else:
        session_key = get_random_bytes(32)
        sub_key = RSA.import_key(open('sub_key.pem').read())
        cipher_rsa = PKCS1_OAEP.new(sub_key)
        enc_session_key = cipher_rsa.encrypt(session_key)
        response = struct.pack(">4s", enc_session_key)
    yield

    yield response


def verify_control_hash(control_hash, random_word, client_secret_seq):
    h = SHA256.new()
    h.update((random_word + client_secret_seq).encode('utf-8'))
    return control_hash == h.hexdigest()