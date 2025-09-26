# gui/dashboard.py
import tkinter as tk
from utils.helpers import chunk_list

# Colors for class cards
COLORS = ["#1abc9c", "#3498db", "#9b59b6", "#e74c3c", "#f39c12", "#16a085"]

class Dashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # ====== TOPBAR ======
        topbar = tk.Frame(self, height=50, bg="#f5f5f5")
        topbar.pack(fill="x")

        tk.Label(topbar, text="Dashboard", font=("Arial", 16, "bold"), bg="#f5f5f5").pack(side="left", padx=12)

        tk.Button(topbar, text="Refresh", command=self.on_refresh).pack(side="right", padx=8)
        tk.Button(topbar, text="Logout", command=self.on_logout).pack(side="right", padx=8)

        # Lecturer name label (center heading)
        self.name_label = tk.Label(self, text="Welcome, Lecturer", font=("Arial", 20, "bold"))
        self.name_label.pack(pady=20)

        # Frame to hold class buttons
        self.grid_frame = tk.Frame(self)
        self.grid_frame.pack(padx=20, pady=10, fill="both", expand=True)

    def load_profile(self, profile, lecturer_email):
        """
        Display lecturer welcome message and classes
        """
        # Fetch lecturer name
        lecturer_name = profile.get("name", "").strip()
        if not lecturer_name:
            lecturer_name = lecturer_email.split("@")[0].capitalize()

        self.name_label.config(text=f"Welcome, {lecturer_name}")

        # Normalize classes from profile
        raw_classes = profile.get("classes", [])

        classes = []
        if isinstance(raw_classes, dict):
            # Firebase dict → keys are class names
            classes = list(raw_classes.keys())
        elif isinstance(raw_classes, list):
            for item in raw_classes:
                if isinstance(item, str):
                    classes.append(item)
                elif isinstance(item, dict) and "name" in item:
                    classes.append(item["name"])

        # Clear previous widgets
        for w in self.grid_frame.winfo_children():
            w.destroy()

        if not classes:
            tk.Label(self.grid_frame, text="No classes assigned.", font=("Arial", 14)).pack()
            return

        # Create grid of class cards (3 columns)
        columns = 3
        rows = list(chunk_list(classes, columns))
        for r, row in enumerate(rows):
            for c, cls in enumerate(row):
                idx = r * columns + c
                color = COLORS[idx % len(COLORS)]

                btn = tk.Button(
                    self.grid_frame,
                    text=cls,
                    bg=color,
                    fg="white",
                    font=("Arial", 12, "bold"),
                    width=22,
                    height=5,
                    command=lambda x=cls: self.open_class(x)
                )
                btn.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")

        # Make columns expand equally
        for c in range(columns):
            self.grid_frame.grid_columnconfigure(c, weight=1)

    def open_class(self, class_name):
        print(f"Opening class: {class_name}")
        self.controller.open_class_screen(class_name)

    def on_refresh(self):
        """Reload the lecturer’s profile"""
        email = self.controller.lecturer.get("email")
        if not email:
            return
        # Call controller to reload profile
        self.controller.reload_dashboard(email)

    def on_logout(self):
        """Handle logout and go back to login"""
        self.controller.lecturer = None
        self.controller.show_frame("login")
