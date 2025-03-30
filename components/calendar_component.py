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

def creds_to_dict(creds):
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
    if 'credentials' not in session:
        return redirect(url_for('calendar_bp.authorize'))
    
    creds = Credentials(**session['credentials'])
    service = build('calendar', 'v3', credentials=creds)
    
    time_min = '1970-01-01T00:00:00Z'
    # Retrieve calendar entries (each with a URL and a color)
    calendar_entries = session.get('calendar_entries', DEFAULT_CUSTOMIZATION['calendar_entries'])
    all_events = []
    
    for entry in calendar_entries:
        url = entry.get('url')
        color = entry.get('color', '#007aff')
        calendar_id = None
        if url.startswith("https://calendar.google.com/calendar/embed?"):
            parsed = urlparse(url)
            qs = parse_qs(parsed.query)
            calendar_id = qs.get("src", [None])[0]
        elif url.startswith("https://calendar.google.com/calendar/u/"):
            parsed = urlparse(url)
            qs = parse_qs(parsed.query)
            calendar_id = qs.get("cid", [None])[0]
        else:
            calendar_id = url
        
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
            if calendar_id != "primary" and "@" in calendar_id:
                try:
                    events_result = service.events().list(
                        calendarId="primary",
                        timeMin=time_min,
                        singleEvents=True,
                        orderBy='startTime'
                    ).execute()
                    calendar_id = "primary"
                except Exception as e2:
                    print(f"Error fetching events for calendar {calendar_id} (fallback primary): {e2}")
                    continue
            else:
                print(f"Error fetching events for calendar {calendar_id}: {e}")
                continue
        
        events = events_result.get('items', [])
        # Attach the selected color to each event
        for event in events:
            event['color'] = color
        all_events.extend(events)
    
    all_events.sort(key=lambda e: e['start'].get('dateTime', e['start'].get('date', '')))
    
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
    from google_auth_oauthlib.flow import Flow
    flow = Flow.from_client_secrets_file(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '../client_secret.json'),
        scopes=['https://www.googleapis.com/auth/calendar.readonly'],
        redirect_uri=url_for('calendar_bp.oauth2callback', _external=True, _scheme='https'))
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    session['state'] = state
    return redirect(authorization_url)

@calendar_bp.route('/oauth2callback')
def oauth2callback():
    state = session.get('state')
    flow = Flow.from_client_secrets_file(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '../client_secret.json'),
        scopes=['https://www.googleapis.com/auth/calendar.readonly'],
        state=state,
        redirect_uri=url_for('calendar_bp.oauth2callback', _external=True, _scheme='https'))
    
    flow.fetch_token(authorization_response=request.url)
    creds = flow.credentials

    # Check if the refresh_token is missing
    if not creds.refresh_token:
        # Option 1: Force re-authentication by clearing existing credentials
        session.pop('credentials', None)
        # Optionally flash a message here to notify the user.
        return redirect(url_for('calendar_bp.authorize'))

    session['credentials'] = creds_to_dict(creds)
    return redirect(url_for('calendar_bp.show_calendar'))
