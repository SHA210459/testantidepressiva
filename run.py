from app import app
from extensions import socketio

app.debug = True  # Wichtig, damit socketio.run() nicht meckert

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, allow_unsafe_werkzeug=True)
