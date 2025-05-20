from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from extensions import socketio
from flask_socketio import emit, join_room, leave_room
import uuid
from models import db, PrivateMessage

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

    # Sende die Nachricht an alle Clients mit user_id
    emit('receive_message', {
        'msg': message,
        'username': username,
        'time': timestamp,
        'color': color,
        'replyTo': reply_to,
        'message_id': message_id,
        'profile_image': current_user.profile_image,
        'is_admin': current_user.is_admin(),
        'user_id': current_user.id  # User-ID hinzufügen für private Chats
    }, broadcast=True)

@socketio.on('react_message')
def handle_react_message(data):
    message_id = data.get('message_id')
    emoji = data.get('emoji')
    username = data.get('username')
    
    print(f"Reaktion erhalten: {username} reagierte mit {emoji} auf Nachricht {message_id}")
    
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

# Private Chat Funktionalitäten
@chat_bp.route('/private/<int:user_id>')
@login_required
def redirect_to_private_chat(user_id):
    """Weiterleitung zum privaten Chat mit einem bestimmten Benutzer"""
    # Sicherstellen, dass der Benutzer existiert
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, username FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    
    if not user:
        flash('Benutzer nicht gefunden', 'danger')
        return redirect(url_for('chat.chat'))
    
    # Zur private_chats-Seite weiterleiten und den Partner-ID als Parameter übergeben
    return redirect(url_for('chat.private_chats') + f'?partner_id={user_id}')

@chat_bp.route('/private_chats')
@login_required
def private_chats():
    """Seite für private Chats anzeigen"""
    partner_id = request.args.get('partner_id', type=int)
    
    # Chat-Partner aus der Datenbank abrufen
    # Entweder vorhandene Chat-Partner oder alle Benutzer
    chat_partners = PrivateMessage.get_chat_partners(current_user.id)
    
    # Wenn keine Chat-Partner gefunden wurden, alle Benutzer außer dem aktuellen abrufen
    if not chat_partners:
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, username, profile_image 
            FROM users 
            WHERE id != %s AND is_banned = 0
        """, (current_user.id,))
        chat_partners = cursor.fetchall()
        cursor.close()
    
    # Wenn ein Partner ausgewählt wurde, dessen Daten holen
    selected_partner = None
    if partner_id:
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, username, profile_image
            FROM users
            WHERE id = %s
        """, (partner_id,))
        selected_partner = cursor.fetchone()
        cursor.close()
    
    return render_template('private_chats.html', 
                           chat_partners=chat_partners,
                           selected_partner=selected_partner)

@chat_bp.route('/get_user_id_by_name/<username>')
@login_required
def get_user_id_by_name(username):
    """Gibt die User-ID für einen Benutzernamen zurück"""
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    
    if user:
        return jsonify({'user_id': user['id']})
    else:
        return jsonify({'error': 'User not found'}), 404

@chat_bp.route('/send_message', methods=['POST'])
@login_required
def send_message():
    """REST-Endpunkt zum Senden privater Nachrichten"""
    data = request.json
    receiver_id = data.get('receiver_id')
    message = data.get('message')
    
    if not receiver_id or not message:
        return jsonify({'error': 'Unvollständige Daten'}), 400
    
    cursor = db.cursor()
    
    try:
        # Ändern von 'content' zu 'message'
        cursor.execute("""
            INSERT INTO private_messages (sender_id, receiver_id, message) 
            VALUES (%s, %s, %s)
        """, (current_user.id, receiver_id, message))
        db.commit()
        message_id = cursor.lastrowid
        
        return jsonify({
            'success': True,
            'message_id': message_id,
            'timestamp': datetime.now().strftime('%H:%M')
        })
    except Exception as e:
        db.rollback()
        print(f"Fehler beim Speichern der Nachricht: {str(e)}")  # Logging hinzufügen
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()

# Socket.IO-Ereignisse für private Chats
@socketio.on('join_private_room')
def handle_join_private_room(data):
    """Benutzer tritt einem privaten Chat-Raum bei"""
    partner_id = data.get('partner_id')
    if partner_id:
        # Erstelle einen eindeutigen Raumnamen (immer gleiche Sortierung für zwei Benutzer)
        room = f"private_{min(current_user.id, partner_id)}_{max(current_user.id, partner_id)}"
        join_room(room)
        print(f"Benutzer {current_user.username} ist dem Raum {room} beigetreten")

@socketio.on('leave_private_room')
def handle_leave_private_room(data):
    """Benutzer verlässt einen privaten Chat-Raum"""
    partner_id = data.get('partner_id')
    if partner_id:
        room = f"private_{min(current_user.id, partner_id)}_{max(current_user.id, partner_id)}"
        leave_room(room)
        print(f"Benutzer {current_user.username} hat den Raum {room} verlassen")

@socketio.on('send_private_message')
def handle_private_message(data):
    """Behandelt das Senden privater Nachrichten"""
    receiver_id = data.get('receiver_id')
    message = data.get('message')
    
    if not receiver_id or not message:
        return
    
    # Raum für die private Unterhaltung bestimmen
    room = f"private_{min(current_user.id, receiver_id)}_{max(current_user.id, receiver_id)}"
    
    # Nachricht in Datenbank speichern
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO private_messages (sender_id, receiver_id, content) 
        VALUES (%s, %s, %s)
    """, (current_user.id, receiver_id, message))
    db.commit()
    message_id = cursor.lastrowid
    cursor.close()
    
    # Nachricht an den Raum senden
    emit('private_message', {
        'message_id': message_id,
        'sender_id': current_user.id,
        'receiver_id': receiver_id,
        'message': message,
        'timestamp': datetime.now().strftime('%H:%M'),
        'sender_name': current_user.username,
        'sender_avatar': current_user.profile_image
    }, room=room)

@chat_bp.route('/delete_chat/<int:partner_id>', methods=['DELETE'])
@login_required
def delete_chat(partner_id):
    """Löscht alle Nachrichten zwischen dem aktuellen Benutzer und dem Partner"""
    try:
        # Verbindung zur Datenbank herstellen
        cursor = db.cursor()
        
        # Alle Nachrichten zwischen den Benutzern löschen
        cursor.execute("""
            DELETE FROM private_messages 
            WHERE (sender_id = %s AND receiver_id = %s)
               OR (sender_id = %s AND receiver_id = %s)
        """, (current_user.id, partner_id, partner_id, current_user.id))
        
        # Chat-Session löschen, falls vorhanden
        user1_id = min(current_user.id, partner_id)
        user2_id = max(current_user.id, partner_id)
        cursor.execute("""
            DELETE FROM chat_sessions
            WHERE user1_id = %s AND user2_id = %s
        """, (user1_id, user2_id))
        
        db.commit()
        cursor.close()
        
        return jsonify({'success': True, 'message': 'Chat wurde gelöscht'}), 200
    except Exception as e:
        print(f"Fehler beim Löschen des Chats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/get_messages/<int:partner_id>')
@login_required
def get_messages(partner_id):
    """API-Endpunkt zum Abrufen von privaten Nachrichten zwischen zwei Benutzern"""
    try:
        # Nachrichten zwischen den Benutzern abrufen
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT pm.id, pm.sender_id, pm.receiver_id, pm.message, 
                   pm.timestamp, pm.is_read, 
                   u_sender.username as sender_name,
                   u_sender.profile_image as sender_avatar
            FROM private_messages pm
            JOIN users u_sender ON pm.sender_id = u_sender.id
            WHERE (pm.sender_id = %s AND pm.receiver_id = %s)
               OR (pm.sender_id = %s AND pm.receiver_id = %s)
            ORDER BY pm.timestamp ASC
        """, (current_user.id, partner_id, partner_id, current_user.id))
        
        messages = cursor.fetchall()
        
        # Formatiere Datum/Zeit für JSON
        for msg in messages:
            if isinstance(msg['timestamp'], datetime):
                msg['timestamp'] = msg['timestamp'].strftime('%H:%M')
        
        # Als ungelesen markierte Nachrichten als gelesen markieren
        unread_ids = [msg['id'] for msg in messages 
                      if msg['is_read'] == 0 and msg['receiver_id'] == current_user.id]
        
        if unread_ids:
            # Markiere Nachrichten als gelesen
            format_str = ','.join(['%s'] * len(unread_ids))
            cursor.execute(f"UPDATE private_messages SET is_read = 1 WHERE id IN ({format_str})",
                          tuple(unread_ids))
            db.commit()
            
        cursor.close()
        return jsonify(messages)
        
    except Exception as e:
        print(f"Fehler beim Laden der Nachrichten: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
