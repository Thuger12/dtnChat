import logging
import socket 
import struct
import time
import threading
import datetime
from datetime import datetime as dt

import requests
import websocket

from _defaults import *


logger = logging.getLogger("client")
logger.setLevel(logging.DEBUG)

info_handler = logging.StreamHandler()
info_handler.setLevel(logging.INFO)

info_formatter = logging.Formatter('%(name)s --- %(levelname)s --- %(message)s')
info_handler.setFormatter(info_formatter)

logger.addHandler(info_handler)


def id_require(f):
    def wrapper(self, *ar, **kwr):
        if self._id:
            return f(self, ar, kwr)
        else:
            return "No id yet"
    return wrapper


def session_key_require(f):
    def wrapper(self, *ar, **kwr):
        if self._session_key:
            return f(self, ar, kwr)
        else:
            return "No session key, login first"
    return wrapper


class Client():
    
    def __init__(self):
        try:
            with open("client_id.txt", 'r') as t:
                self._id = int(t.readline())
        except FileNotFoundError:
            self._id = None
        self._session_key = b""
        self._own_room_id = None

    def registration(self, name):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.connect((REGISTRATION_HOST, REGISTRATION_PORT))
            logger.info("Establish connection")

            body_len = len(name.encode())
            l = struct.pack('>I', body_len)
            body = struct.pack(f'>{body_len}s', name.encode())

            sock.send(l + body)

            response = sock.recv(1024)
            sock.close()
            logger.info("Connection closed")
            self._id = struct.unpack('>I', response)[0]
            self._save_id()
            return "Registration complete" 
        except Exception as e:
            sock.close()
            logger.warning(e)
            return "Try again"

    @id_require
    def login(self):
        print("LOGIN")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.connect((LOGIN_HOST, LOGIN_PORT))
            logger.info("Establish connection")
            
            body_len = len(str(self._id).encode())
            l = struct.pack('>I', body_len)
            body = struct.pack(f'>{body_len}s', str(self._id).encode())
            sock.send(l + body)

            response = sock.recv(1024)
            sock.close()
            logger.info("Connection closed")
            self._session_key = response
            return "Login complete"
        except Exception as e:
            sock.close()
            logger.warning(e)
            return "Try again"

    @session_key_require
    def create_room(self, room_settings):
        headers = {"id": str(self._id),
                   "session_key": self._session_key}
        print(room_settings)
        try:
            result = requests.post(f"http://{SERVER_ADDR}/room/create", headers = headers, json = room_settings)
        except Exception as e:
            raise e
        else:
            return result.json()

    @session_key_require
    def connect_to_room(self, room_id):
        """ 
        To get message in real time we need to implement 
        thread to not block receive message while client
        enter message
        """

        def recv(ws):
            while True:
                recv = ws.recv()
                print(recv)
                time.sleep(0.5)
                
        def write(ws):
            while True:
                msg = input("Enter message: ")
                ws.send(msg)
                time.sleep(0.5)
                
        try:
            ws = websocket.WebSocket()
            ws.connect(WS_URI.format(room_id), header=[f"id:{self._id}",
                                                       f"session_key:{self._session_key}"])
            recv_thread = threading.Thread(target=recv, args=(ws,))
            write_thread = threading.Thread(target=write, args=(ws,))
            
            recv_thread.start()
            write_thread.start()
            
            
        except Exception:
            ws.close()
            return "Connection closed"

    def _save_id(self):
        try:
            with open("client_id.txt", 'w') as ci:
                ci.write(str(self._id))
        except Exception as e:
            logger.warning(e)
            return "Try again"


def registration(client: Client):
    client_name = input("Enter your name: ")
    result = client.registration(client_name)
    print(result)
    return


def login(client: Client):
    result = client.login()
    print(result)


def create_room(client: Client):
    room_settings = {}
    room_settings["name"] = input("Room name: ")
    room_settings["password"] = input("Room password: ")
    result = client.create_room(room_settings)
    print(result)


def connect_to_room(client: Client):
    room_id = input("What room id you want to connect: ")
    result = client.connect_to_room(room_id)
    print(result)


funcs = {1: registration,
         2: login,
         3: create_room,
         4: connect_to_room,
         5: exit}


if __name__ == "__main__":
    client = Client()
    while True:
        try:
            n = int(input("Choose one: \n1)Registration\n2)Login\n3)Create room\n4)Get into room\n"))
            if n not in funcs:
                continue
            funcs.get(n)(client)
        except KeyboardInterrupt as e:
            exit()


    exit()

