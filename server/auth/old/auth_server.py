import asyncio
import socket
import sys
import selectors


from message_handler import MessageHandler
from registration import process_registration
from login import process_login
from _defaults import *


message_handler_event = {8080: process_registration,
                         8090: process_login}


selector = selectors.DefaultSelector()


def create_socket(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind((host, port))
    except sock.error as e:
        return
    sock.listen()
    print(f'Socket binded and listening on {host} host and {port} port')
    sock.setblocking(False)
    selector.register(sock, selectors.EVENT_READ, data=None)
    return 


def accept_connection(sock):
    connection, client_address = sock.accept()
    db_conn = 'psycopg2.connect(DSN)'
    print(f'Socket accepting new connection from {client_address}')
    connection.setblocking(False)
    message_handler = MessageHandler(selector, 
                                     connection, 
                                     client_address,
                                     message_handler_event[sock.getsockname()[1]],
                                     db_conn)

    selector.register(connection, selectors.EVENT_READ, data=message_handler)


if __name__ == '__main__':
    # Creating socket by every auth process
    # Login and registration
    create_socket(HOST, REG_PORT)
    create_socket(HOST, LOGIN_PORT)

    try:
        while True:
            events = selector.select(timeout=None)
            for key, mask in events:
                print(key, mask)
                if key.data is None:
                    accept_connection(key.fileobj)
                else:
                    message_handler = key.data
                    try:
                        message_handler.process_connection(mask)
                    except StopIteration:
                        pass
                    except OSError:
                        pass
                    except Exception as e:
                        print(e)
                        print('While processing')
                        message_handler.close()
    except KeyboardInterrupt:
        print('Keyboard interrupt')
    finally:
        selector.close()
        key.fileobj.close()


a

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    ser
