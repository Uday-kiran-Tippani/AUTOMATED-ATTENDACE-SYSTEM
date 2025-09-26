# gui/components/menu.py
import tkinter as tk
from tkinter import ttk

class SidebarMenu(ttk.Frame):
    def __init__(self, parent, controller, menu_items=None):
        super().__init__(parent, width=200)
        self.controller = controller
        self.pack_propagate(False)  # prevent frame from resizing to fit contents

        # Default menu items if none provided
        if menu_items is None:
            menu_items = [
                {"label": "Dashboard", "command": lambda: controller.show_frame("dashboard")},
                {"label": "Classes", "command": lambda: controller.show_frame("class")},
                {"label": "Logout", "command": self.logout},
            ]

        # Title / App name
        title = ttk.Label(self, text="Lecturer Panel", font=("Arial", 14, "bold"))
        title.pack(pady=20)

        # Buttons
        for item in menu_items:
            btn = ttk.Button(self, text=item["label"], command=item["command"])
            btn.pack(fill="x", pady=5, padx=10)

    def logout(self):
        """Handle logout and go back to login screen."""
        self.controller.lecturer = None
        self.controller.show_frame("login")
