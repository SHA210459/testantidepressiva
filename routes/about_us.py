from flask import Blueprint, render_template

# Create a Blueprint for the About Us page
about_us_bp = Blueprint('about_us', __name__)

@about_us_bp.route('/aboutus')
def about_us():
    return render_template('aboutus.html')