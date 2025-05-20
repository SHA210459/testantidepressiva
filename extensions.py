from flask_socketio import SocketIO

# Erstelle SocketIO-Instanz ohne app (wird später verknüpft)
socketio = SocketIO(cors_allowed_origins="*", ping_timeout=60, ping_interval=25)
