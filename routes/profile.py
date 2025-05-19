from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from models import User

profile_bp = Blueprint('profile', __name__)

# Verzeichnis für Profilbilder
UPLOAD_FOLDER = 'static/profile_pics/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Funktion zum Prüfen der erlaubten Dateitypen
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Formulardaten abrufen
        username = request.form['username']
        color = request.form['color']
        password = request.form.get('password', None)
        profile_image = request.form.get('current_profile_image', None)

        # Überprüfen, ob ein neues Profilbild hochgeladen wurde
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Speichern des Bildes im Upload-Ordner
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                profile_image = 'profile_pics/' + filename  # Speichere nur den relativen Pfad
        if not profile_image:
            profile_image = "profile_pics/default_profile_image.png"  # Standardbild, wenn kein Bild hochgeladen wurde

        # Profil aktualisieren
        User.update_profile(current_user.id, username, color, password, profile_image)
        flash('Profil erfolgreich aktualisiert', 'success')
        return redirect(url_for('main.home'))

    # Benutzerdaten abrufen
    user = User.get_by_id(current_user.id)
    return render_template('profile.html', user=user)