from flask import Blueprint, render_template, request, redirect, url_for, session
from config import DEFAULT_CUSTOMIZATION

customization_bp = Blueprint('customization_bp', __name__,
                             template_folder='../templates')

@customization_bp.route('/customize', methods=['GET', 'POST'])
def customize():
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
            
        try:
            session['slide_duration'] = int(request.form.get('slide_duration', DEFAULT_CUSTOMIZATION['slide_duration']))
        except ValueError:
            session['slide_duration'] = DEFAULT_CUSTOMIZATION['slide_duration']

        # Process calendar entries (multiple)
        calendar_urls = request.form.getlist('calendar_urls')
        calendar_colors = request.form.getlist('calendar_colors')
        calendar_entries = []
        for url, color in zip(calendar_urls, calendar_colors):
            if url.strip():
                calendar_entries.append({'url': url.strip(), 'color': color.strip() if color.strip() else '#007aff'})
        if not calendar_entries:
            calendar_entries = DEFAULT_CUSTOMIZATION['calendar_entries']
        session['calendar_entries'] = calendar_entries

        return redirect(url_for('customization_bp.customize'))

    current_settings = {
        'background_color': session.get('background_color', DEFAULT_CUSTOMIZATION['background_color']),
        'button_color': session.get('button_color', DEFAULT_CUSTOMIZATION['button_color']),
        'container_color': session.get('container_color', DEFAULT_CUSTOMIZATION['container_color']),
        'font_color': session.get('font_color', DEFAULT_CUSTOMIZATION['font_color']),
        'preview_size': session.get('preview_size', 'medium'),
        'slideshow_timeout': session.get('slideshow_timeout', 300),
        'slide_duration': session.get('slide_duration', DEFAULT_CUSTOMIZATION['slide_duration']),
        'calendar_entries': session.get('calendar_entries', DEFAULT_CUSTOMIZATION['calendar_entries']),
    }

    return render_template('customize.html', **current_settings)