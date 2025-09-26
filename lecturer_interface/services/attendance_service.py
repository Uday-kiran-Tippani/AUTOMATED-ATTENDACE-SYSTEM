# services/attendance_service.py
from config.google_sheets_config import init_gspread
from datetime import date
from typing import List, Dict
import gspread
import smtplib
from email.mime.text import MIMEText
from services.lecturer_service import get_assigned_classes

# Lazy initialize gspread client once
_gc = None

# MASTER SPREADSHEET NAME
MASTER_SHEET_NAME = "Master Attendance Sheet"


def _get_client():
    global _gc
    if _gc is None:
        _gc = init_gspread()
    return _gc


def get_master_sheet() -> gspread.Spreadsheet:
    """Open the master spreadsheet."""
    gc = _get_client()
    try:
        sh = gc.open(MASTER_SHEET_NAME)
    except gspread.SpreadsheetNotFound:
        sh = gc.create(MASTER_SHEET_NAME)
        print(f"[INFO] Created Master Sheet: {MASTER_SHEET_NAME}")
    return sh


def get_or_create_class_tab(
    sh: gspread.Spreadsheet, class_name: str, students: List[Dict], lecturer_email: str
) -> gspread.Worksheet:
    """
    Ensure a worksheet exists for this lecturer+class combo.
    """
    # Derive safe lecturer identifier (before @)
    lecturer_key = lecturer_email.split("@")[0]
    sheet_name = f"{class_name}_{lecturer_key}"

    try:
        ws = sh.worksheet(sheet_name)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=sheet_name, rows="500", cols="50")
        ws.update("A1:D1", [["Roll", "Name", "Total", "Percentage"]])

        if students:
            rows = [[s["roll"], s["name"]] for s in students]
            ws.update(f"A2:B{len(rows)+1}", rows)

            for i in range(2, len(rows) + 2):
                ws.update_acell(f"C{i}", f'=COUNTIF(E{i}:Z{i},"P")')
                ws.update_acell(f"D{i}", f'=IF(C{i}=0,0,C{i}/COUNTA(E$1:Z$1)*100)')

    return ws


def mark_attendance(
    lecturer_email: str, class_name: str, students_present: List[str], students_master: List[Dict]
) -> bool:
    """Mark attendance for a lecturer in the master sheet."""
    sh = get_master_sheet()
    ws = get_or_create_class_tab(sh, class_name, students_master, lecturer_email)

    today = date.today().isoformat()

    # Get header row
    header = ws.row_values(1)

    # Check if today's date already exists in header
    if today in header:
        col_index = header.index(today) + 1
    else:
        col_index = len(header) + 1
        ws.update_cell(1, col_index, today)

    # Map rolls to rows
    rolls = ws.col_values(1)[1:]  # skip header
    values = [["P"] if r in students_present else ["A"] for r in rolls]

    # Write attendance in today’s column
    start = 2
    end = start + len(values) - 1
    cell_range = (
        gspread.utils.rowcol_to_a1(start, col_index)
        + ":"
        + gspread.utils.rowcol_to_a1(end, col_index)
    )
    ws.update(cell_range, values)

    # Send email summary (now includes Google Sheet link)
    send_attendance_email(lecturer_email, class_name, today, values, rolls, sh.url)
    return True


def send_attendance_email(
    lecturer_email: str,
    class_name: str,
    today: str,
    values: List[List[str]],
    rolls: List[str],
    sheet_url: str,
):
    """Send attendance summary email to lecturer with sheet link."""
    present_count = sum(1 for v in values if v[0] == "P")
    total = len(rolls)
    absent_count = total - present_count

    msg_content = (
        f"Attendance Summary for {class_name} on {today}\n\n"
        f"Total Students: {total}\n"
        f"Present: {present_count}\n"
        f"Absent: {absent_count}\n\n"
        f"You can view the full attendance sheet here:\n{sheet_url}"
    )

    msg = MIMEText(msg_content)
    msg["Subject"] = f"Attendance Summary - {class_name} ({today})"
    msg["From"] = "your-email@gmail.com"
    msg["To"] = lecturer_email

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login("adikavinannayauniversitystaff@gmail.com", "eblx ovrz ibzu prlo")  # ⚠️ use app password
            server.send_message(msg)
    except Exception as e:
        print(f"[WARNING] Failed to send email: {e}")
