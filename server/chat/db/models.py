from datetime import datetime


class Message():
    @staticmethod
    async def add(msg_list, db_connection):
        insert_messages_query = """INSERT INTO message (room_id, client_id, send_time, message_data) VALUES($1, $2, $3, $4);"""
        await db_connection.execute(insert_messages_query, msg_list)

    @staticmethod
    async def get(client_id, room_id, db_connection):
        select_messages_query = """SELECT * FROM message WHERE client_id = $1 AND room_id = $2 ORDER BY send_time;"""
        result = await db_connection.fetchall(select_messages_query, client_id, room_id)
        return dict(result)


class Client():
    def __init__(self):
        pass

    @staticmethod
    async def create(client_information, db_connection):
        create_client_query = """INSERT INTO client(name, registration_time) VALUES($1, $2)"""
        await db_connection.execute(create_client_query, client_information.get("name"), datetime.today())
    
    @staticmethod
    async def get_information(client_id, db_connection):
        """ Returning dict with client information as keys

        :return: dict
        """

        get_information_query = """SELECT * FROM client WHERE client_id = $1"""
        client_information = await db_connection.fetchrow(get_information_query, client_id)
        return dict(client_information)

    @staticmethod
    async def add_room(client_id, room_id, db_connection):
        add_room_query = """UPDATE client SET room_id = $1 WHERE client_id = $2"""
        await db_connection.execute(add_room_query, room_id, client_id)


class Room():
    @staticmethod
    async def create(room_id, room_name, password, client_id, db_connection):
        transaction = db_connection.transaction()
        await transaction.start()
        try:
            sql_create_room = '''INSERT INTO room(room_id, name, password, admin_id) VALUES($1, $2, $3, $4)'''
            await db_connection.execute(sql_create_room, 
                                        (room_id,
                                         room_name,
                                         password,
                                         client_id))
        except Exception as e:
            await transaction.rollback()
            raise e
        else:
            await transaction.commit()
        return 

    @staticmethod
    async def add_participant(room_id, user_id, db_connection):
        async with db_connection.transaction():
            sql_add_participant = '''INSERT INTO room_participant(room_id, user_id) VALUES($1, $2)'''
            await db_connection.execute(sql_add_participant, room_id, user_id)
        return 

    @staticmethod
    async def delete_participant(room_id, user_id, db_connection):
        async with db_connection.transaction():
            sql_delete_participant = '''DELETE FROM room_participant(room_id, user_id) VALUES($1, $2)'''
            await db_connection.execute(sql_delete_participant, room_id, user_id)
        return 
