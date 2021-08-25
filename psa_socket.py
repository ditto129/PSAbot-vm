from flask_socketio import SocketIO,emit, join_room, leave_room
from flask import jsonify


print('----------import psa socket-----------')

socketio = SocketIO()
def init_socketio(app):
    print('---------- init psa socket-----------')
    socketio.init_app(app,cors_allowed_origins="*")
    
@socketio.on('connect')
def test_connect():
    print('---------- connected -----------')
    emit('connect', 'server says connected.')

@socketio.on('connect_event')
def connected_msg(msg):
    print('---------- connect_event -----------')
    print(type(msg))
    print(msg)
    emit('server_response',msg)
    
@socketio.on('join_room')
def join_chat_room(data):
    print('---------- join_room -----------')
    print(data)
    join_room('room01')
    emit('room_msg', data['id'] + ' has entered the room.', to='room01')
    emit('room_msg', data['id'] + ' you cannot see me.', to='room02')
    
    
    