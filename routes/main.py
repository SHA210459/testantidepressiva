from flask import Blueprint, render_template
from flask_login import login_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/home')
@login_required  # Dies stellt sicher, dass nur eingeloggte Benutzer die Seite sehen können
def home():
    return render_template('home.html')  # home.html sollte im templates-Ordner liegen
