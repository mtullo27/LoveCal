# lovecal/components/customization.py

from flask import Blueprint, render_template, request, redirect, url_for, session
import os

from config import DEFAULT_CUSTOMIZATION

customization_bp = Blueprint('customization_bp', __name__,
                             template_folder='../templates')

@customization_bp.route('/customize', methods=['GET', 'POST'])
def customize():
    """
    Allows the user to customize interface colors, preview size,
    slideshow timeout, and calendar URLs (multiple supported via dynamic textboxes).
    Auto-submits on change for color inputs and submits normally for others.
    """
    if request.method == 'POST':
        # Colors
        session['background_color'] = request.form.get('background_color', DEFAULT_CUSTOMIZATION['background_color'])
        session['button_color'] = request.form.get('button_color', DEFAULT_CUSTOMIZATION['button_color'])
        session['container_color'] = request.form.get('container_color', DEFAULT_CUSTOMIZATION['container_color'])
        session['font_color'] = request.form.get('font_color', DEFAULT_CUSTOMIZATION['font_color'])

        # Additional settings
        session['preview_size'] = request.form.get('preview_size', 'medium')
        try:
            session['slideshow_timeout'] = int(request.form.get('slideshow_timeout', 300))
        except ValueError:
            session['slideshow_timeout'] = 300

        # Calendar URLs: get list of inputs; strip empty entries
        calendar_urls_list = request.form.getlist('calendar_urls')
        calendar_urls_list = [url.strip() for url in calendar_urls_list if url.strip()]
        if not calendar_urls_list:
            calendar_urls_list = [DEFAULT_CUSTOMIZATION['calendar_url']]
        session['calendar_urls'] = calendar_urls_list

        return redirect(url_for('customization_bp.customize'))

    # GET request: render the form with current settings.
    calendar_urls_list = session.get('calendar_urls', [DEFAULT_CUSTOMIZATION['calendar_url']])
    current_settings = {
        'background_color': session.get('background_color', DEFAULT_CUSTOMIZATION['background_color']),
        'button_color': session.get('button_color', DEFAULT_CUSTOMIZATION['button_color']),
        'container_color': session.get('container_color', DEFAULT_CUSTOMIZATION['container_color']),
        'font_color': session.get('font_color', DEFAULT_CUSTOMIZATION['font_color']),
        'preview_size': session.get('preview_size', 'medium'),
        'slideshow_timeout': session.get('slideshow_timeout', 300),
        'calendar_urls': calendar_urls_list,
    }

    return render_template('customize.html', **current_settings)
