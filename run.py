from app import create_app, socketio  # Import create_app and socketio
from flask_socketio import SocketIO

# Create the Flask app
app = create_app()

# Run the app with socketio
if __name__ == '__main__':
    socketio.run(app, debug=True)
