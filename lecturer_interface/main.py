# main.py
import tkinter as tk
from config.firebase_config import init_firebase
from config.google_sheets_config import init_gspread
from gui.login_screen import LoginScreen
from gui.dashboard import Dashboard
from gui.class_screen import ClassScreen
from gui.attendance_screen import AttendanceScreen
from services.lecturer_service import refresh_lecturer_classes

# Initialize Firebase and gspread
try:
    init_firebase()
except ValueError:
    pass  # ignore duplicate initialization

# Optional: validate Sheets credentials at startup
# init_gspread()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Lecturer Attendance Interface")
        self.geometry("1100x720")
        self.lecturer = None  # {"email":..., "profile":...}

        # frames registry
        self.frames = {}
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        # instantiate frames
        self.frames["login"] = LoginScreen(container, self)
        self.frames["dashboard"] = Dashboard(container, self)
        self.frames["class"] = ClassScreen(container, self)
        self.frames["attendance"] = AttendanceScreen(container, self)

        for f in self.frames.values():
            f.place(relwidth=1, relheight=1)

        self.show_frame("login")

    def show_frame(self, key: str):
        """Bring the selected frame to the front."""
        frame = self.frames.get(key)
        if frame:
            frame.tkraise()

    def login_successful(self, email: str):
        """Call this when login succeeds."""
        # Fetch lecturer profile from service
        profile = refresh_lecturer_classes(email)
        self.lecturer = {"email": email, "profile": profile}

        # Load dashboard
        self.show_dashboard_for(profile)

    def show_dashboard_for(self, profile: dict):
        """Load lecturer profile into dashboard."""
        email = self.lecturer["email"] if self.lecturer else profile.get("email", "")
        self.frames["dashboard"].load_profile(profile, email)
        self.show_frame("dashboard")

    def open_class_screen(self, class_name: str):
        """Open the class screen for a given class."""
        self.frames["class"].load_class(class_name)
        self.show_frame("class")

    def open_attendance_screen(self, class_name: str, students_dict: dict):
        """Open the attendance screen with student list."""
        lecturer_email = self.lecturer["email"] if self.lecturer else ""
        self.frames["attendance"].load(class_name, students_dict, lecturer_email)
        self.show_frame("attendance")


if __name__ == "__main__":
    app = App()
    app.mainloop()
