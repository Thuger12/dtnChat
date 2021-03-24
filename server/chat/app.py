#! /usr/bin/env python

import asyncio
import logging

import asyncpg
from aiohttp import web

from routes import routes_post, routes_get, routes_delete
from settings import *
from middleware import middleware


logger = logging.getLogger("server")
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


async def create_app():
        app = web.Application()

        # Dict to store room id and all users connections
        app.rooms_participants = {}

        app.add_routes([web.get(x[0], x[1]) for x in routes_get])
        app.add_routes([web.post(x[0], x[1]) for x in routes_post])
        app.add_routes([web.delete(x[0], x[1]) for x in routes_delete])
        app.on_cleanup.append(on_cleanup)
        logger.info("Chat is running")
        return app


async def on_cleanup(app):
    for participants_list in app.rooms_participants.values():
            for participant in participants_list.values():
                    await participant.send_str('Server close')
                    await participant.close(code=1001, message='Server shutdown')




