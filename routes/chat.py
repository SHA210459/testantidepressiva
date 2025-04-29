from flask import Blueprint, render_template
from flask_login import login_required
from datetime import datetime
from extensions import socketio
from flask_socketio import emit
import uuid

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/')
@login_required
def chat():
    return render_template('chat.html')

@socketio.on('send_message')
def handle_send_message(data):
    username = data.get('username')
    message = data.get('msg')
    color = data.get('color')
    reply_to = data.get('replyTo')
    timestamp = datetime.now().strftime('%H:%M')
    message_id = str(uuid.uuid4())

    emit('receive_message', {
        'msg': message,
        'username': username,
        'time': timestamp,
        'color': color,
        'replyTo': reply_to,
        'message_id': message_id,
        'reactions': []
    }, broadcast=True)

@socketio.on('react_message')
def handle_react_message(data):
    message_id = data.get('message_id')
    emoji = data.get('emoji')
    username = data.get('username')

    emit('react_message', {
        'message_id': message_id,
        'emoji': emoji,
        'username': username
    }, broadcast=True)
