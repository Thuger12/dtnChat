import asyncio
import os
import struct
import datetime
import logging

import asyncpg

from _defaults import *


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

info_handler = logging.StreamHandler()
info_handler.setLevel(logging.INFO) 
info_formatter = logging.Formatter('%(name)s --- %(levelname)s --- %(message)s')
info_handler.setFormatter(info_formatter)

warning_handler = logging.FileHandler('log.py')
warning_handler.setLevel(logging.WARNING)
warning_formatter = logging.Formatter('%(name)s !!! %(levelname)s !!! %(message)s')
warning_handler.setFormatter(warning_formatter)

logger.addHandler(info_handler)
logger.addHandler(warning_handler)


class Request():
    def __init__(self, reader):
        self._recv_buffer = b""
        self.body = None
        self.len = 0

        self._reader = reader

    async def read(self):
        await self._read_to_buffer()
        self._process_request_len()
        self._process_request()
    
    async def _read_to_buffer(self):
        try:
            self._recv_buffer = await self._reader.read(2048)
        except Exception as e:
            raise e
    
    def _process_request_len(self):
        if len(self._recv_buffer) >= MSG_LEN_LENGTH:
            self.len = struct.unpack('>I', self._recv_buffer[:MSG_LEN_LENGTH])[0]
            self._recv_buffer = self._recv_buffer[MSG_LEN_LENGTH:]

    def _process_request(self):
        if not len(self._recv_buffer) >= self.len:
            raise Exception('Len of of recieved message is less than it should')
        self.body = struct.unpack(f'>{self.len}s', self._recv_buffer[:self.len])[0].decode()

    def __repr__(self):
        return f"{self.len}, {self.body}"


async def serve_registration(reader, writer):
    connection = writer.get_extra_info('socket')
    peername = connection.getpeername()
    logger.info(f"New connection from {peername} for registration")
    try: 
        request = Request(reader)
        await request.read()

        logger.info("DB connection open")
        db_connection = await asyncpg.connect(DSN)
        await db_connection.execute("INSERT INTO client(name, registration_time) VALUES($1, $2)", 
                                    request.body, datetime.date.today())
        result = await db_connection.fetchrow("SELECT (client_id) FROM client WHERE name = $1", 
                                              request.body)
        await db_connection.close()
        logger.info("DB connection close")

        # Packing client id into 4 bytes
        client_id = dict(result)['client_id']
        resp = struct.pack('>I', client_id)

        writer.write(resp)
        # No writing till buffer is full
        await writer.drain() 
        writer.close()
        await writer.wait_closed()
        logger.info(f"Connection from {peername} closed")
    except Exception as e:
        raise e
        logger.warning(e)
        writer.close() 
        if not db_connection.is_closed():
            await db_connection.close()
            logger.info("DB connection close")


async def serve_login(reader, writer):
    connection = writer.get_extra_info('socket')
    peername = connection.getpeername()
    logger.info(f"New connection from {peername} for login")
    try:
        request = Request(reader)
        await request.read()
        client_id = int(request.body)

        session_key = os.urandom(SESSION_KEY_LEN)

        logger.info(f"DB connection for {peername} open")
        db_connection = await asyncpg.connect(DSN)
        await db_connection.execute("UPDATE client SET session_key = $1 WHERE client_id = $2", session_key, client_id)
        await db_connection.close()
        logger.info(f"DB connection for {peername} close")
        
        writer.write(session_key)
        await writer.drain()
        writer.close()
        await writer.wait_closed()
        logger.info(f"Connection from {peername} closed")
        return 
    except Exception as e:
        logger.warning(e)
        writer.close()
        if not db_connection.is_closed():
            await db_connection.close()
            logger.info("DB connection close")


    

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    server1 = loop.run_until_complete(asyncio.start_server(serve_registration, 'localhost', 8020))
    server2 = loop.run_until_complete(asyncio.start_server(serve_login, 'localhost', 8010))
    print(server1, server2)
    logger.info("Servers for login and registration has started")
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt")
        loop.close()
    except Exception as e:
        logger.warning("Exception occured")
        loop.close()
        logger.info("Loop has been closed")
