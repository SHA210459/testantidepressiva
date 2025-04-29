from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import User, db

admin_bp = Blueprint('admin', __name__)

# Admin-Dashboard (Benutzerverwaltung) für alle eingeloggten Benutzer
@admin_bp.route('/')
@login_required
def dashboard():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, username, role FROM users")
    users = cursor.fetchall()
    cursor.close()

    return render_template('admin_dashboard.html', users=users)

# Benutzerrolle ändern (nur für Admins)
@admin_bp.route('/change_role/<int:user_id>', methods=['POST'])
@login_required
def change_role(user_id):
    if current_user.role != 'admin':
        flash('Du hast keine Berechtigung, die Rolle zu ändern!', 'error')
        return redirect(url_for('admin.dashboard'))

    new_role = request.form['role']
    cursor = db.cursor()
    cursor.execute("UPDATE users SET role = %s WHERE id = %s", (new_role, user_id))
    db.commit()
    cursor.close()

    flash(f"Rolle des Benutzers erfolgreich auf {new_role} geändert!", 'success')
    return redirect(url_for('admin.dashboard'))

# Benutzer löschen (nur für Admins)
@admin_bp.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash('Du hast keine Berechtigung, Benutzer zu löschen!', 'error')
        return redirect(url_for('admin.dashboard'))

    cursor = db.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    db.commit()
    cursor.close()

    flash('Benutzer erfolgreich gelöscht!', 'success')
    return redirect(url_for('admin.dashboard'))
