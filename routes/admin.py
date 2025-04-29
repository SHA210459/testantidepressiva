from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db

admin_bp = Blueprint('admin', __name__)

# Admin-Dashboard anzeigen (für alle eingeloggten Nutzer)
@admin_bp.route('/')
@login_required
def dashboard():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, username, role, is_banned FROM users")
    users = cursor.fetchall()
    cursor.close()
    return render_template('admin_dashboard.html', users=users)

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
    if current_user.role != 'admin':
        flash('Keine Berechtigung!', 'error')
        return redirect(url_for('admin.dashboard'))

    new_role = request.form['role']
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
    if current_user.role != 'admin':
        flash('Keine Berechtigung!', 'error')
        return redirect(url_for('admin.dashboard'))

    ban_status = request.form.get('is_banned') == 'true'
    cursor = db.cursor()
    cursor.execute("UPDATE users SET is_banned = %s WHERE id = %s", (ban_status, user_id))
    db.commit()
    cursor.close()
    flash('Benutzerstatus aktualisiert.', 'success')
    return redirect(url_for('admin.dashboard'))

# Benutzer löschen (nur Admin)
@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash('Keine Berechtigung!', 'error')
        return redirect(url_for('admin.dashboard'))

    cursor = db.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    db.commit()
    cursor.close()
    flash('Benutzer gelöscht.', 'success')
    return redirect(url_for('admin.dashboard'))
