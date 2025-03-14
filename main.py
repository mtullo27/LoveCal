# lovecal/main.py

from flask import Flask, session
from components.photo_curation import photo_bp
from components.customization import customization_bp
from components.calendar_component import calendar_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = 'super_secret_key'  # replace with a secure key

    # Register your blueprints
    app.register_blueprint(photo_bp, url_prefix='/')
    app.register_blueprint(customization_bp, url_prefix='/')
    app.register_blueprint(calendar_bp, url_prefix='/')

    return app

if __name__ == '__main__':
    application = create_app()
    application.run(host='0.0.0.0', port=5000, debug=True)
