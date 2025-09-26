# from config.firebase_config import init_firebase
# from services.student_service import get_students_for_class

# # Make sure Firebase is initialized
# init_firebase()

# students = get_students_for_class("b_tech_i")
# for s in students:
#     print(s["roll_number"], s["name"])


import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Define scope
scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

# Load credentials
creds = ServiceAccountCredentials.from_json_keyfile_name('config/google_service_account.json', scope)
gc = gspread.authorize(creds)

# Open the master sheet
sheet = gc.open("Master Attendance Sheet")
print("Sheets in Master:", sheet.worksheets())
