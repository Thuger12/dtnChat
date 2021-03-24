import os
from sys import argv

from aiohttp.web import run_app
from aiomisc import bind_socket
from app import create_app


def main():
    sock = bind_socket(address='localhost', port=9000)
    app = create_app()
    run_app(app, sock=sock)

if __name__ == '__main__':
    main()
