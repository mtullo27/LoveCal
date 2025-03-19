# lovecal/components/calendar_component.py

import os
import datetime
from flask import Blueprint, render_template, session, redirect, url_for, request
from config import DEFAULT_CUSTOMIZATION
from urllib.parse import urlparse, parse_qs

# Google API imports
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

calendar_bp = Blueprint('calendar_bp', __name__,
                        template_folder='../templates')

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
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
    Displays events from multiple calendars using the Google Calendar API.
    Supports both personal calendars and public calendar links.
    If not yet authorized, it redirects to the OAuth flow.
    """
    if 'credentials' not in session:
        return redirect(url_for('calendar_bp.authorize'))
    
    creds = Credentials(**session['credentials'])
    service = build('calendar', 'v3', credentials=creds)
    
    time_min = '1970-01-01T00:00:00Z'
    # Retrieve calendar entries from session; default to the one from configuration.
    calendar_entries = session.get('calendar_urls', [DEFAULT_CUSTOMIZATION['calendar_url']])
    all_events = []
    
    for entry in calendar_entries:
        calendar_id = None
        if entry.startswith("https://calendar.google.com/calendar/embed?"):
            # Public embed link with "src" parameter
            parsed = urlparse(entry)
            qs = parse_qs(parsed.query)
            calendar_id = qs.get("src", [None])[0]
        elif entry.startswith("https://calendar.google.com/calendar/u/"):
            # Public calendar link with "cid" parameter
            parsed = urlparse(entry)
            qs = parse_qs(parsed.query)
            calendar_id = qs.get("cid", [None])[0]
        else:
            # Assume it's a direct calendar ID. If it contains "@" it likely refers to your personal calendar.
            calendar_id = entry
        
        if not calendar_id:
            continue
        
        try:
            events_result = service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
        except Exception as e:
            # If the error occurs for what appears to be a personal calendar (contains '@'),
            # try using "primary" as a fallback.
            if calendar_id != "primary" and "@" in calendar_id:
                try:
                    events_result = service.events().list(
                        calendarId="primary",
                        timeMin=time_min,
                        singleEvents=True,
                        orderBy='startTime'
                    ).execute()
                    # Update calendar_id to primary for clarity in logs.
                    calendar_id = "primary"
                except Exception as e2:
                    print(f"Error fetching events for calendar {calendar_id} (fallback primary): {e2}")
                    continue
            else:
                print(f"Error fetching events for calendar {calendar_id}: {e}")
                continue
        
        events = events_result.get('items', [])
        all_events.extend(events)
    
    # Optionally sort the combined events by start time.
    all_events.sort(key=lambda e: e['start'].get('dateTime', e['start'].get('date', '')))
    
    # Update credentials in session (in case they were refreshed)
    session['credentials'] = creds_to_dict(creds)
    
    customization = {
        'background_color': session.get('background_color', DEFAULT_CUSTOMIZATION['background_color']),
        'button_color': session.get('button_color', DEFAULT_CUSTOMIZATION['button_color']),
        'container_color': session.get('container_color', DEFAULT_CUSTOMIZATION['container_color']),
        'font_color': session.get('font_color', DEFAULT_CUSTOMIZATION['font_color']),
    }
    
    return render_template('calendar.html',
                           customization=customization,
                           events=all_events)

@calendar_bp.route('/authorize')
def authorize():
    """
    Starts the OAuth 2.0 flow for Google Calendar access.
    """
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for('calendar_bp.oauth2callback', _external=True))
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')
    
    session['state'] = state
    return redirect(authorization_url)

@calendar_bp.route('/oauth2callback')
def oauth2callback():
    """
    Handles the OAuth 2.0 callback and stores credentials.
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
