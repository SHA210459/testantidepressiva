from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

@profile_bp.route('/view')
@login_required
def view_profile():
    return render_template('profile.html', user=current_user)

# Füge die Route für die Profilaktualisierung hinzu
@profile_bp.route('/update', methods=['GET', 'POST'])
@login_required
def update_profile():
    if request.method == 'POST':
        # Hier könntest du den Code hinzufügen, um die Benutzerinformationen zu aktualisieren
        current_user.username = request.form['username']
        current_user.save()  # Oder eine entsprechende Methode zum Speichern der Daten
        return redirect(url_for('profile.view_profile'))  # Leitet nach der Aktualisierung zurück zum Profil
    return render_template('update_profile.html', user=current_user)
