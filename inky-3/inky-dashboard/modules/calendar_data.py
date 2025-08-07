"""
Improved Google Calendar data fetcher with proper token management.
Handles automatic token refresh and secure credential storage.
"""

import sys
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

class GoogleCalendarClient:
    def __init__(self):
        self.auth_dir = Path(__file__).parent.parent / "auth"
        self.auth_dir.mkdir(exist_ok=True)
        
        self.credentials_path = self.auth_dir / "google_credentials.json"
        self.token_path = self.auth_dir / "google_token.json"
        
        self._service = None
        self._credentials = None
    
    def _load_credentials(self):
        """Load existing credentials from token file."""
        if self.token_path.exists():
            try:
                self._credentials = Credentials.from_authorized_user_file(
                    str(self.token_path), SCOPES
                )
                return True
            except Exception as e:
                print(f"[ERROR] Failed to load credentials: {e}")
        return False
    
    def _save_credentials(self):
        """Save credentials to token file."""
        if self._credentials:
            try:
                with open(self.token_path, 'w') as token:
                    token.write(self._credentials.to_json())
                print("[INFO] Google credentials saved successfully")
            except Exception as e:
                print(f"[ERROR] Failed to save credentials: {e}")
    
    def _refresh_credentials(self):
        """Refresh expired credentials using refresh token."""
        if (self._credentials and 
            self._credentials.expired and 
            self._credentials.refresh_token):
            try:
                self._credentials.refresh(Request())
                self._save_credentials()
                print("[INFO] Google credentials refreshed successfully")
                return True
            except Exception as e:
                print(f"[ERROR] Failed to refresh credentials: {e}")
                return False
        return False
    
    def _authenticate_new_user(self):
        """Perform initial OAuth flow for new user."""
        if not self.credentials_path.exists():
            raise FileNotFoundError(
                f"Google credentials file not found at {self.credentials_path}. "
                "Please download it from Google Cloud Console."
            )

        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(self.credentials_path), SCOPES
            )
            # Set access_type to 'offline' to get refresh token
            flow.authorization_url(access_type='offline', prompt='consent')
            self._credentials = flow.run_local_server(port=0)
            self._save_credentials()
            print("[INFO] New Google authentication completed")
            return True
        except Exception as e:
            print(f"[ERROR] Authentication failed: {e}")
            return False
    
    def _ensure_authenticated(self):
        """Ensure we have valid credentials, refreshing or re-authenticating as needed."""
        # Try to load existing credentials
        if not self._load_credentials():
            return self._authenticate_new_user()
        
        # Check if credentials are valid
        if not self._credentials.valid:
            if not self._refresh_credentials():
                # Refresh failed, need to re-authenticate
                return self._authenticate_new_user()
        
        return True
    
    def get_service(self):
        """Get authenticated Google Calendar service."""
        if not self._service:
            if not self._ensure_authenticated():
                raise Exception("Failed to authenticate with Google Calendar")
            
            try:
                self._service = build('calendar', 'v3', credentials=self._credentials)
            except Exception as e:
                print(f"[ERROR] Failed to build Calendar service: {e}")
                raise
        
        return self._service
    
    def get_calendar_events(self, days_ahead=30, max_results=10):
        """Fetch upcoming Google Calendar events."""
        try:
            service = self.get_service()
            
            now = datetime.utcnow().isoformat() + 'Z'
            end = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + 'Z'
            
            events_result = service.events().list(
                calendarId='primary',
                timeMin=now,
                timeMax=end,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            calendar_data = {}
            
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                time = start[11:16] if 'T' in start else "All Day"
                summary = event.get('summary', 'No title')
                date = start.split("T")[0]
                
                calendar_data.setdefault(date, []).append({
                    "time": time,
                    "summary": summary
                })
            
            return calendar_data
            
        except HttpError as e:
            if e.resp.status == 401:
                # Token might be invalid, try to refresh
                print("[WARNING] Received 401, attempting to refresh credentials")
                self._credentials = None
                self._service = None
                return self.get_calendar_events(days_ahead, max_results)
            else:
                print(f"[ERROR] Google Calendar API error: {e}")
                return {}
        except Exception as e:
            print(f"[ERROR] Failed to fetch calendar events: {e}")
            return {}

# Global client instance
_calendar_client = None

def get_calendar_client():
    """Get singleton calendar client."""
    global _calendar_client
    if _calendar_client is None:
        _calendar_client = GoogleCalendarClient()
    return _calendar_client

def get_calendar_events():
    """Fetch upcoming Google Calendar events (backward compatibility)."""
    return get_calendar_client().get_calendar_events()

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

__all__ = ["get_calendar_events", "next_daniel_day", "get_calendar_client"]
