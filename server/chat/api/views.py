import hashlib
import logging
import time
from datetime import datetime
import uuid

from aiohttp import web, WSMsgType
from aiohttp.web import json_response

from chat.db import models


logger = logging.getLogger(f"server.{__name__}")


class User():
    @staticmethod
    async def get_information(request):
        client_id = int(request.match_info.get("client_id"))
        client_information = await models.Client.get_information(client_id, request.app.db_connection)
        print(client_information)
        return json_response({"client_information": ""})


class Room():
    """

    Description:
    -Room represents place where clients recv and send msg
    -It stores participants in db
    -Open for connection from others

    """
    
    @staticmethod
    async def create(request):
        app = request.app
        client_id = int(request.headers.get("id"))
        room_settings = await request.json()

        new_room_id = uuid.uuid1()
        app.rooms_participants[new_room_id] = {}

        #passw = hashlib.sha256()
        #passw.update(room_settings["password"].encode("utf-8"))
        #await models.Room.create(new_room_id, 
        #                         room_settings["name"], 
        #                         passw.hexdigest, 
        #                         client_id, 
        #                         app.db_connection)

        ## Adding room id to user for tracking his own room
        #await models.Client.add_room(room_name, new_room_id, passw, client_id, app.db_connection)

        return json_response({"msg": f"Room {new_room_id} created"})

    @staticmethod
    async def delete(request):
        app = request.app
        client_id = request.headers.get("id")
        delete_room_id = request.match_info["room_id"]
        
        req_body = await request.json()
        
        room_password = await models.Room.get_password(delete_room_id, app.db_connection)
        if not room_password == req_body["password"]:
            return json_response({"msg": "Wrong password"})
        await models.Room.delete(client_id, delete_room_id, app.db_connection)
        if delete_room_id not in app.rooms:
            return json_response({"msg": "Room doesnt exists"})
        del app.room[delete_room_id]
        return json_response({"msg": "Deleted"})

    @staticmethod
    async def get_into(request):
        """ Adding user connection to room dict and room participant """

        app = request.app

        # TODO: get a real id of client
        client_id = int(request.headers.get("id"))
        room_id = int(request.match_info.get("room_id"))
        #client_information = await models.Client.get_information(client_id, app.db_connection)

        #await models.Room.add_participant(room_id, client_id, app.db_connection)
        ws = web.WebSocketResponse()

        # Get http request and make ws connection
        await ws.prepare(request)
        logger.info("Got new websocket connection")
        
        app.rooms_participants[room_id][client_id] = ws

        # Insert one message will coast a lot
        # It's better to write a chunk of messages
        # For example 10
        msg_list = []
        await Room._broadcast_message(app.rooms_participants[room_id].values(), f"New user {client_information.get('name')} connected")
        while True:
            try:
                msg = await ws.receive()
                if msg.type == WSMsgType.TEXT:
                    if msg.data == "close":
                        logger.info("Close message recieved")
                        del app.rooms_participants[room_id][client_id]
                        await ws.close()
                    else:
                        print(msg)
                        msg_list.append([room_id, client_id, 
                                         datetime.today(), msg.data])
                        #if len(msg_list) == 10:
                        #    models.Message.add(msg_list, app.db_connection)
                        #    msg_list = []
                        await Room._broadcast_message(app.rooms_participants[room_id].values(), msg.data)
                elif msg.type == WSMsgType.ERROR:
                    logger.info("Error message")
                    raise Exception("WS msg type error")
            except Exception as e:
                raise e
            finally:
                del app.rooms_participants[room_id][client_id]
                await Room._broadcast_message(app.rooms_participants[room_id].values(), f'User disconnected')
                await ws.close()
                logger.info("Delete user from room")
        return json_response({'message': 'Your connection closed'})

    @staticmethod
    async def _broadcast_message(participant_list, message: str):
        for participant_conn in participant_list: 
            await participant_conn.send_str(message)

    @staticmethod
    async def get_information(request):
        # TODO: get room information from db
        pass


