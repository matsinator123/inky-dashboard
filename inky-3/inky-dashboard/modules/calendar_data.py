"""
Google Calendar data fetcher for the dashboard.
Fetches upcoming events and finds the next "Daniel" event.
"""

import os
import pickle
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
TOKEN_PATH = 'auth/token.pickle'
CREDENTIALS_PATH = 'auth/credentials.json'

def get_calendar_events():
    """Fetch upcoming Google Calendar events for the next 30 days."""
    creds = None

    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    now = datetime.utcnow().isoformat() + 'Z'
    end = (datetime.utcnow() + timedelta(days=30)).isoformat() + 'Z'

    events_result = service.events().list(
        calendarId='primary', timeMin=now, timeMax=end,
        maxResults=10, singleEvents=True, orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    calendar_data = {}
    for e in events:
        start = e['start'].get('dateTime', e['start'].get('date'))
        time = start[11:16] if 'T' in start else "All Day"
        summary = e.get('summary', 'No title')
        date = start.split("T")[0]
        calendar_data.setdefault(date, []).append({"time": time, "summary": summary})

    return calendar_data

def next_daniel_day():
    """Return the number of days until the next event with 'daniel' in the summary."""
    events = get_calendar_events()
    today = datetime.now().date()
    for offset in range(0, 30):
        check_date = str(today + timedelta(days=offset))
        if check_date in events:
            for event in events[check_date]:
                if "daniel" in event["summary"].lower():
                    return offset
    return None

__all__ = ["get_calendar_events", "next_daniel_day"]
