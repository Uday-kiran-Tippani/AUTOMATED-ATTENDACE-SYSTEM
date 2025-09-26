# services/master_sheet_service.py
import gspread
from config.google_sheets_config import init_gspread
from services.lecturer_service import get_assigned_classes
from services.student_service import get_students_for_class

MASTER_SHEET_NAME = "Master Attendance Sheet"

def initialize_master_sheet():
    """
    Create or update the master spreadsheet:
    - Create a sheet per class in Firebase
    - Add all students in columns A/B
    - Add all lecturers assigned to that class as headers in columns starting D
    """
    gc = init_gspread()

    # Open or create master sheet
    try:
        sh = gc.open(MASTER_SHEET_NAME)
        print(f"[INFO] Master sheet found: {MASTER_SHEET_NAME}")
    except gspread.SpreadsheetNotFound:
        sh = gc.create(MASTER_SHEET_NAME)
        print(f"[INFO] Master sheet created: {MASTER_SHEET_NAME}")

    # Fetch all classes (replace this with actual admin/HOD list later)
    all_classes = set()
    lecturers_emails = ["hod@example.com"]  # TODO: replace with dynamic list

    for lec_email in lecturers_emails:
        classes = get_assigned_classes(lec_email)["classes"]
        for c in classes:
            all_classes.add(c["name"])

    # Process each class
    for class_name in all_classes:
        students = get_students_for_class(class_name)

        # Gather lecturers for this class
        lecturers = []
        for lec_email in lecturers_emails:
            lec_classes = get_assigned_classes(lec_email)["classes"]
            for c in lec_classes:
                if c["name"] == class_name:
                    lecturers.append(lec_email)

        # Create or get worksheet
        try:
            ws = sh.worksheet(class_name)
            print(f"[INFO] Class tab exists: {class_name}")
        except gspread.WorksheetNotFound:
            ws = sh.add_worksheet(title=class_name, rows="500", cols="50")
            print(f"[INFO] Created class tab: {class_name}")

        # Update students (columns A/B)
        ws.update("A1:B1", [["Roll", "Name"]])
        if students:
            rows = [[s["roll_number"], s["name"]] for s in students]
            ws.append_rows(rows)

        # Update lecturers header (start from column D)
        header = ws.row_values(1)
        for i, lec in enumerate(lecturers):
            col_index = 4 + i  # D=4
            if lec not in header:
                ws.update_cell(1, col_index, lec)

    print("[INFO] Master sheet initialization complete.")
