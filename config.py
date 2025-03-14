# lovecal/config.py

import os

# Paths & default values
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'slideshow_images')
METADATA_FILE = os.path.join(UPLOAD_FOLDER, 'metadata.json')

# Default customization settings
DEFAULT_CUSTOMIZATION = {
    'background_color': '#f9f9f9',
    'button_color': '#007aff',
    'container_color': '#ffffff',
    'font_color': '#333333',
    'preview_size': 'medium',     # small / medium / large
    'slideshow_timeout': 300,     # in seconds
    'calendar_url': 'https://calendar.google.com',  # default
}
