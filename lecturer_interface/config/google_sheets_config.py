# config/google_sheets_config.py
import gspread
from google.oauth2.service_account import Credentials
import os

GOOGLE_SERVICE_ACCOUNT = os.path.join("config", "google_service_account.json")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def init_gspread():
    """
    Returns an authorized gspread client.
    Place your Google service account JSON file at config/google_service_account.json
    """
    creds = Credentials.from_service_account_file(GOOGLE_SERVICE_ACCOUNT, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client
