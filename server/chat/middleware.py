import asyncpg
from aiohttp import web
import logging
from aiohttp.web import middleware, json_response, HTTPBadRequest
from typing import Optional
from aiohttp.web_request import Request
from asyncpg import exceptions
from settings import *


logger = logging.getLogger("server.middleware")


async def check_session_key(request):
    client_id = int(request.headers['client_id'])
    client_session_key = request.headers['client_id']
    print(request.headers)
    db_conn = request.app.db_connection
    result = await db_conn.fetchrow("SELECT session_key FROM client WHERE client_id = $1", client_id)
    print(result)
    if not result:
        raise HTTPBadRequest
    return client_session_key == dict(result)["session_key"]


@middleware
async def middleware(request: Request, handler):

    """ Main middleware

    -- Open and close db connection per request
    -- Catch all exceptions in code
    -- Check user id

    """

    try:
        request.app.db_connection = await asyncpg.connect(DB_PG_URL)
        logger.info(f"Create db connection for the {request.host}")
        if not await check_session_key(request):
            print("Not the same")
        response = await handler(request)
    except HTTPBadRequest as br:
        raise br
        return json_response({"msg": br})
    except Exception as e:
        raise e
        return json_response({"msg": e})
    else:
        await request.app.db_connection.close()
        logger.info(f"Close db connection for the {request.host}")
        return response





