# lovecal/components/photo_curation.py

import os
import json
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, send_from_directory, session
from config import UPLOAD_FOLDER, METADATA_FILE, DEFAULT_CUSTOMIZATION

photo_bp = Blueprint('photo_bp', __name__,
                     template_folder='../templates')

# Make sure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Load metadata if available
if os.path.exists(METADATA_FILE):
    with open(METADATA_FILE, 'r') as f:
        metadata = json.load(f)
else:
    metadata = {}

def save_metadata():
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=4)

@photo_bp.route('/', methods=['GET', 'POST'])
def index():
    """
    Main route: upload images (POST), display gallery (GET).
    """
    if request.method == 'POST':
        files_uploaded = request.files.getlist('file')
        for file in files_uploaded:
            if file.filename == '':
                continue
            if file:
                file_path = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(file_path)
                metadata[file.filename] = {
                    'upload_time': datetime.now().isoformat(),
                    'caption': "",
                    'tags': ""
                }
        save_metadata()
        return redirect(url_for('photo_bp.index'))

    # Build file list
    files = [f for f in os.listdir(UPLOAD_FOLDER)
             if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

    # Sorting
    sort_by = request.args.get('sort', 'upload_date')
    if sort_by == 'name':
        files.sort(key=lambda x: x.lower())
    else:
        # sort by upload_time desc
        files.sort(key=lambda x: metadata.get(x, {}).get('upload_time', ''), reverse=True)

    # Retrieve user custom settings from session
    customization = {
        'background_color': session.get('background_color', DEFAULT_CUSTOMIZATION['background_color']),
        'button_color': session.get('button_color', DEFAULT_CUSTOMIZATION['button_color']),
        'container_color': session.get('container_color', DEFAULT_CUSTOMIZATION['container_color']),
        'font_color': session.get('font_color', DEFAULT_CUSTOMIZATION['font_color']),
        'preview_size': session.get('preview_size', 'medium'),
    }

    return render_template('index.html', 
                           files=files, 
                           metadata=metadata,
                           customization=customization)

@photo_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded images."""
    return send_from_directory(UPLOAD_FOLDER, filename)

@photo_bp.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    """Delete an image and remove its metadata."""
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        if filename in metadata:
            del metadata[filename]
            save_metadata()
        return '', 200
    else:
        return 'File not found', 404

@photo_bp.route('/edit', methods=['POST'])
def edit_metadata():
    """Update caption/tags for a specified image."""
    filename = request.form.get('filename')
    caption = request.form.get('caption', '')
    tags = request.form.get('tags', '')
    if filename in metadata:
        metadata[filename]['caption'] = caption
        metadata[filename]['tags'] = tags
        save_metadata()
        return '', 200
    else:
        return 'File not found', 404

@photo_bp.route('/slideshow')
def slideshow():
    # Load images from the slideshow_images folder
    files = [f for f in os.listdir(UPLOAD_FOLDER)
             if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
    
    # Retrieve user custom settings (background, font, etc.)
    customization = {
        'background_color': session.get('background_color', DEFAULT_CUSTOMIZATION['background_color']),
        'button_color': session.get('button_color', DEFAULT_CUSTOMIZATION['button_color']),
        'container_color': session.get('container_color', DEFAULT_CUSTOMIZATION['container_color']),
        'font_color': session.get('font_color', DEFAULT_CUSTOMIZATION['font_color']),
    }

    return render_template('slideshow.html',
                           files=files,
                           customization=customization)

