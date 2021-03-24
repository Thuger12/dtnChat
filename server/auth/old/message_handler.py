import selectors
import struct
import time


from login import process_login
from _defaults import *


selectors_mode = {'r': selectors.EVENT_READ,
                  'w': selectors.EVENT_WRITE}


class MessageHandler():
    def __init__(self, selector, connection, client_addr, process_handler, db_conn):
        print('New handler')
        self.selector = selector
        self.connection = connection
        self.client_addr = client_addr

         # Coroutine that will save state of registration stage
        self._process_handler = process_handler(db_conn)
        
        self._recv_buffer = b""
        self._request_len = None
        self._request = None

        self._send_buffer = b""
        self._response_ready = None

        # Attrs to skip situation of two writes or read in a row
        # From both: client and server
        self._server_turn = 0

       

    def _set_selector_event(self, mode):
        '''Set selector listen to particular mode: r, w, r+w'''
        print("Change selector event")
        self.selector.modify(self.connection, selectors_mode.get(mode), data=self)

    def _change_turn(self):
        self._server_turn = 1 if self._server_turn == 0 else 0

    def process_connection(self, mask):
        # When main func calls that, socket already ready to read or write 
        if mask & selectors.EVENT_READ and not self._server_turn:
            self.read()
        elif mask & selectors.EVENT_WRITE:
            self.write()
        else:
            raise Exception('One of the side send 2 messages in a row')

    def read(self):
        print("read func")
        self._read_to_buffer()
        self._process_request_len()
        self._process_request()
        self._change_turn()
        try:
            self._process_handler.send(self._recv_buffer)
        except StopIteration:
            raise StopIteration('Process handler finish his job')
            self.close()
        else:
            self._recv_buffer = b''
            self._set_selector_event('w')
            return

    def write(self):
        """
        Send signal about ready to write to process_handler
        If it's ready with response, write it to the buffer
        And then send to client
        """
        print("In write")
        self._create_response()
        if self._response_ready:
            self._write()
        self._clean_response()
        self._change_turn()
        self._set_selector_event('r')

    def _read_to_buffer(self):
        try:
            data = self.connection.recv(1024)
            print(data.decode())
        except BlockingIOError:
            raise BlockingIOError('Socket blockes while trying to recieve message')
        else:
            if data:
                self._recv_buffer += data
                return
            else:
                print('Error')
                raise Exception

    def _process_request(self):
        print("Process request")
        if not len(self._recv_buffer) >= self._request_len:
            raise Exception('Len of of recieved message is less than it should')
        self.request_body = self._recv_buffer[:self._request_len]

    def _process_request_len(self):
        print('Process request len')
        if len(self._recv_buffer) >= MSG_LEN_LENGTH:
            print(self._recv_buffer)
            self._request_len = struct.unpack('>I', self._recv_buffer[:MSG_LEN_LENGTH])[0]
            print(self._request_len)
            self._recv_buffer = self._recv_buffer[MSG_LEN_LENGTH:]

    def _write(self):
        if self._send_buffer:
            try:
                send = self.connection.send(self._send_buffer)
            except BlockingIOError:
                raise BlockingIOError('Socket blocked while trying to send message')
            else:
                self._send_buffer = self._send_buffer[send:]

    def _create_response(self):
        try:
            server_response = self._process_handler.__next__()
        except StopIteration:
            raise StopIteration('Process handler finish his job')
            self._response_ready = None
            return
        self._send_buffer += server_response
        self._response_ready = True

    def _clean_response(self):
        self._send_buffer = b''
        self._response_ready = None

    def close(self):
        print("Message handler closed")
        try:
            self.selector.unregister(self.connection)
        except Exception as e:
            raise e
        try:
            self.connection.close()
        except OSError as e:
            raise e
        finally:
            self.connection = None
