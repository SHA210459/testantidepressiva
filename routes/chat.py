from flask import Blueprint, render_template
from flask_login import login_required
from datetime import datetime
from extensions import socketio  # Importiere SocketIO
from flask_socketio import emit

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/')
@login_required
def chat():
    return render_template('chat.html')

# SocketIO-Events
@socketio.on('send_message')
def handle_send_message(data):
    username = data.get('username')
    message = data.get('msg')
    color = data.get('color')
    reply_to = data.get('replyTo')
    timestamp = datetime.now().strftime('%H:%M')

    # Sende Nachricht an alle verbundenen Clients
    emit('receive_message', {
        'msg': message,
        'username': username,
        'time': timestamp,
        'color': color,
        'replyTo': reply_to
    }, broadcast=True)
