from app import create_app, socketio,db # Import create_app and socketio
from flask_socketio import SocketIO

# Create the Flask app
app = create_app()

# Run the app with socketio
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)
