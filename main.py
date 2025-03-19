from flask import Flask, session
from components.photo_curation import photo_bp
from components.customization import customization_bp
from components.calendar_component import calendar_bp
from datetime import timedelta
from config import DEFAULT_CUSTOMIZATION

def create_app():
    app = Flask(__name__)
    app.secret_key = 'super_secret_key'  # Replace with a secure key
    # Make sessions permanent 
    app.permanent_session_lifetime = timedelta(days=30)


    @app.context_processor
    def inject_customizations():
        return {
            'customization': {
                'background_color': session.get('background_color', DEFAULT_CUSTOMIZATION['background_color']),
                'button_color': session.get('button_color', DEFAULT_CUSTOMIZATION['button_color']),
                'container_color': session.get('container_color', DEFAULT_CUSTOMIZATION['container_color']),
                'font_color': session.get('font_color', DEFAULT_CUSTOMIZATION['font_color'])
            }
        }

    app.register_blueprint(photo_bp, url_prefix='/')
    app.register_blueprint(customization_bp, url_prefix='/')
    app.register_blueprint(calendar_bp, url_prefix='/')

    return app

if __name__ == '__main__':
    application = create_app()
    application.run(host='0.0.0.0', port=5000, debug=True)
