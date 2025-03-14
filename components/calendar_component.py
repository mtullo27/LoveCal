# lovecal/components/calendar_component.py

from flask import Blueprint, render_template, session
from config import DEFAULT_CUSTOMIZATION

calendar_bp = Blueprint('calendar_bp', __name__,
                        template_folder='../templates')

@calendar_bp.route('/calendar')
def show_calendar():
    """
    Displays the user's chosen calendar in an iframe.
    The same customization is applied for background, etc.
    """
    customization = {
        'background_color': session.get('background_color', DEFAULT_CUSTOMIZATION['background_color']),
        'button_color': session.get('button_color', DEFAULT_CUSTOMIZATION['button_color']),
        'container_color': session.get('container_color', DEFAULT_CUSTOMIZATION['container_color']),
        'font_color': session.get('font_color', DEFAULT_CUSTOMIZATION['font_color']),
    }
    calendar_url = session.get('calendar_url', DEFAULT_CUSTOMIZATION['calendar_url'])
    return render_template('calendar.html',
                           customization=customization,
                           calendar_url=calendar_url)
