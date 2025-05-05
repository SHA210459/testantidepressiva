from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from datetime import datetime
from extensions import socketio
from flask_socketio import emit
import uuid

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/')
@login_required
def chat():
    # Prüfen ob Benutzer gesperrt ist
    if hasattr(current_user, 'is_banned') and current_user.is_banned:
        flash('Du bist gesperrt und kannst keine Nachrichten senden.', 'danger')
        
    return render_template('chat.html')

@socketio.on('send_message')
def handle_send_message(data):
    # Blockiere Nachrichten von gesperrten Benutzern
    if hasattr(current_user, 'is_banned') and current_user.is_banned:
        # Sende eine Fehlermeldung zurück an den Client
        emit('banned_message', {
            'message': 'Du bist gesperrt und kannst keine Nachrichten senden.'
        }, broadcast=False, to=request.sid)
        return
    
    username = data.get('username')
    message = data.get('msg')
    color = data.get('color')
    reply_to = data.get('replyTo')
    timestamp = datetime.now().strftime('%H:%M')
    message_id = str(uuid.uuid4())
    
    # Optional: Nachricht in Datenbank speichern
    # cursor = db.cursor()
    # cursor.execute("INSERT INTO messages (user_id, content) VALUES (%s, %s)", 
    #               (current_user.id, message))
    # db.commit()
    # message_id = cursor.lastrowid
    # cursor.close()

    # Sende die Nachricht an alle Clients
    emit('receive_message', {
        'msg': message,
        'username': username,
        'time': timestamp,
        'color': color,
        'replyTo': reply_to,
        'message_id': message_id,
        'profile_image': current_user.profile_image,
        'is_admin': current_user.is_admin()
    }, broadcast=True)

@socketio.on('react_message')
def handle_react_message(data):
    message_id = data.get('message_id')
    emoji = data.get('emoji')
    username = data.get('username')

    # Sende das Emoji-Reaktions-Event an alle Clients
    emit('react_message', {
        'message_id': message_id,
        'emoji': emoji,
        'username': username
    }, broadcast=True)

@socketio.on('delete_message')
def handle_delete_message(data):
    message_id = data.get('message_id')
    
    # Nur Admins oder Nachrichtenersteller dürfen löschen
    if current_user.is_admin():
        emit('message_deleted', {'message_id': message_id}, broadcast=True)
