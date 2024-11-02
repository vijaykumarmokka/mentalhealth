from app import create_app, db
from flask_socketio import SocketIO

app = create_app()
socketio = SocketIO(app)  # Initialize SocketIO with your Flask app

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    socketio.run(app, debug=True) 
