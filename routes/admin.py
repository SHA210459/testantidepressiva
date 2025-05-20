from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, User

admin_bp = Blueprint('admin', __name__)

def is_admin(self):
    # Robuste Implementierung
    try:
        return self.role == 'admin'
    except AttributeError:
        return False

# Admin-Dashboard anzeigen (für alle eingeloggten Nutzer)
@admin_bp.route('/')
@login_required
def dashboard():
    if not current_user.is_admin():
        flash('Keine Berechtigung für den Admin-Bereich!', 'error')
        return redirect(url_for('main.home'))
        
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, username, role, is_banned FROM users")
    users = cursor.fetchall()
    cursor.close()
    return render_template('admin_dashboard.html', users=users, isAdmin=current_user.is_admin())

# Benutzername ändern (nur Admin)
@admin_bp.route('/change_username/<int:user_id>', methods=['POST'])
@login_required
def change_username(user_id):
    if current_user.role != 'admin':
        flash('Keine Berechtigung!', 'error')
        return redirect(url_for('admin.dashboard'))

    new_username = request.form['username']
    cursor = db.cursor()
    cursor.execute("UPDATE users SET username = %s WHERE id = %s", (new_username, user_id))
    db.commit()
    cursor.close()
    flash('Benutzername geändert.', 'success')
    return redirect(url_for('admin.dashboard'))

# Rolle ändern (nur Admin)
@admin_bp.route('/change_role/<int:user_id>', methods=['POST'])
@login_required
def change_role(user_id):
    if not current_user.is_admin():
        flash('Keine Berechtigung!', 'error')
        return redirect(url_for('admin.dashboard'))

    new_role = request.form['role']
    
    # Prüfen, ob der letzte Admin entfernt werden würde
    if new_role != 'admin' and current_user.id == user_id:
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
        admin_count = cursor.fetchone()[0]
        cursor.close()
        
        if admin_count <= 1:
            flash('Der letzte Admin kann nicht entfernt werden!', 'error')
            return redirect(url_for('admin.dashboard'))
    
    cursor = db.cursor()
    cursor.execute("UPDATE users SET role = %s WHERE id = %s", (new_role, user_id))
    db.commit()
    cursor.close()
    flash('Rolle geändert.', 'success')
    return redirect(url_for('admin.dashboard'))

# Benutzer sperren/entsperren (nur Admin)
@admin_bp.route('/toggle_ban/<int:user_id>', methods=['POST'])
@login_required
def toggle_ban(user_id):
    if not current_user.is_admin():
        flash('Keine Berechtigung', 'error')
        return redirect(url_for('main.home'))
    
    # Direkter Datenbankzugriff statt User.get_by_id
    cursor = db.cursor(dictionary=True)
    
    # Prüfe aktuellen Status
    cursor.execute("SELECT username, is_banned FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    
    if user_data:
        # Umkehren des is_banned-Status
        new_status = not user_data['is_banned']
        cursor.execute("UPDATE users SET is_banned = %s WHERE id = %s", (new_status, user_id))
        db.commit()
        
        # Erfolgsmeldung
        status_text = "gesperrt" if new_status else "entsperrt"
        flash(f'Benutzer {user_data["username"]} wurde {status_text}', 'success')
    
    cursor.close()
    return redirect(url_for('admin.dashboard'))

# Benutzer löschen (nur Admin)
@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin():
        flash('Keine Berechtigung!', 'error')
        return redirect(url_for('admin.dashboard'))
    
    try:
        cursor = db.cursor()
        
        # Schritt 1: Chat-Sessions löschen
        cursor.execute("""
            DELETE FROM chat_sessions 
            WHERE user1_id = %s OR user2_id = %s
        """, (user_id, user_id))
        
        # Schritt 2: Private Nachrichten löschen
        cursor.execute("""
            DELETE FROM private_messages 
            WHERE sender_id = %s OR receiver_id = %s
        """, (user_id, user_id))
        
        # Schritt 3: Nachrichtenreaktionen löschen
        cursor.execute("""
            DELETE FROM message_reactions 
            WHERE user_id = %s
        """, (user_id,))
        
        # Schritt 4: Benutzer löschen
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        
        db.commit()
        flash('Benutzer und alle zugehörigen Daten erfolgreich gelöscht.', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Fehler beim Löschen des Benutzers: {str(e)}', 'error')
    finally:
        cursor.close()
        
    return redirect(url_for('admin.dashboard'))
