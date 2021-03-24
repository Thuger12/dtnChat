from chat.api.views import Room, User


routes_get = [
        ('/room/get_information/{room_id}', Room.get_information),
        ('/user/get_information/{user_id}', User.get_information),
        ('/room/get_into/{room_id}', Room.get_into)
]

routes_post = [
        ('/room/create', Room.create),
        
]

routes_delete = [
        ('/room/delete/{room_id}', Room.delete)
]
