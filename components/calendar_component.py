import os
import datetime
from flask import Blueprint, render_template, session, redirect, url_for, request
from config import DEFAULT_CUSTOMIZATION

# Google API imports
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

calendar_bp = Blueprint('calendar_bp', __name__,
                        template_folder='../templates')

# Define the scope for read-only access to your calendar
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# Adjust the path to where your client_secret.json is located
CLIENT_SECRETS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../client_secret.json')

def creds_to_dict(creds):
    """Convert credentials object to a dict to store in session."""
    return {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }

@calendar_bp.route('/calendar')
def show_calendar():
    """
    Displays events from your personal calendar using the Google Calendar API.
    If you aren’t authorized yet, it redirects to the authorization flow.
    """
    if 'credentials' not in session:
        return redirect(url_for('calendar_bp.authorize'))
    
    # Load stored credentials from session
    creds = Credentials(**session['credentials'])
    
    # Build the Google Calendar service
    service = build('calendar', 'v3', credentials=creds)
    
    # Query the Calendar API for upcoming events
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    
    # Update credentials in session (in case they were refreshed)
    session['credentials'] = creds_to_dict(creds)
    
    # Retrieve customization settings from session
    customization = {
        'background_color': session.get('background_color', DEFAULT_CUSTOMIZATION['background_color']),
        'button_color': session.get('button_color', DEFAULT_CUSTOMIZATION['button_color']),
        'container_color': session.get('container_color', DEFAULT_CUSTOMIZATION['container_color']),
        'font_color': session.get('font_color', DEFAULT_CUSTOMIZATION['font_color']),
    }
    
    # Pass the events to the template (you will need to update calendar.html to display these)
    return render_template('calendar.html',
                           customization=customization,
                           events=events)

@calendar_bp.route('/authorize')
def authorize():
    """
    Starts the OAuth 2.0 flow to authorize access to your Google Calendar.
    """
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for('calendar_bp.oauth2callback', _external=True))
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')
    
    # Save the state in session to verify in the callback
    session['state'] = state
    return redirect(authorization_url)

@calendar_bp.route('/oauth2callback')
def oauth2callback():
    """
    Handles the OAuth 2.0 callback and stores the credentials in the session.
    """
    state = session.get('state')
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=state,
        redirect_uri=url_for('calendar_bp.oauth2callback', _external=True))
    
    flow.fetch_token(authorization_response=request.url)
    
    creds = flow.credentials
    session['credentials'] = creds_to_dict(creds)
    
    return redirect(url_for('calendar_bp.show_calendar'))
