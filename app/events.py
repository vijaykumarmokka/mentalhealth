# Import necessary modules
from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from app import socketio

# Define the event handler for 'join' event
@socketio.on('join')
def handle_join(room):
    print(f"{current_user.first_name} joined room: {room}")
    join_room(room)  # Join the specified chat room
    emit('message', {'msg': f'{current_user.first_name} has joined the room.'}, room=room)

# Define the event handler for 'leave' event
@socketio.on('leave')
def handle_leave(room):
    print(f"{current_user.first_name} left room: {room}")
    leave_room(room)  # Leave the specified chat room
    emit('message', {'msg': f'{current_user.first_name} has left the room.'}, room=room)

@socketio.on('send_message')
def handle_message(data):
    print(f"Message received on the server: {data}")  # Debugging print
    first_name = current_user.first_name
    message = data['message']
    room = data['room']
    
    # Emit the message to the specified room
    emit('receive_message', {'username': first_name, 'message': message}, room=room)
    print(f"Message sent to room {room}: {message}")
