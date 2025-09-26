# gui/class_screen.py
import tkinter as tk
from tkinter import ttk, messagebox
from services.student_service import get_students_for_class

class ClassScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Topbar
        topbar = tk.Frame(self, height=50, bg="#f5f5f5")
        topbar.pack(fill="x")
        tk.Button(topbar, text="← Back", command=lambda: controller.show_frame("dashboard")).pack(side="left", padx=8, pady=8)
        self.class_label = tk.Label(topbar, text="", font=("Arial", 14))
        self.class_label.pack(side="left", padx=12)

        # Take Attendance button (center of the screen)
        self.take_btn = tk.Button(self, text="Take Attendance", command=self.on_take_attendance)
        self.take_btn.place(relx=0.5, rely=0.25, anchor="center")

        # Bottom area for student list (50% of screen height)
        bottom = tk.Frame(self)
        bottom.place(relx=0.5, rely=0.55, anchor="n", relwidth=0.9, relheight=0.4)

        cols = ("roll", "name")
        self.tree = ttk.Treeview(bottom, columns=cols, show="headings", height=12)
        for col in cols:
            self.tree.heading(col, text=col.title())
            self.tree.column(col, width=150)
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(bottom, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.current_class = None
        self.students_list = []  # ✅ changed from dict to list

    def load_class(self, class_name):
        """Load students for a class"""
        self.current_class = class_name
        self.class_label.config(text=f"Class: {class_name}")
        self.tree.delete(*self.tree.get_children())

        # Fetch students
        self.students_list = get_students_for_class(class_name)

        if not self.students_list:
            messagebox.showinfo("Info", "No students found for this class.")
            return

        # Display all students (loop list instead of dict)
        for student in self.students_list:
            roll = student.get("roll_number", "")
            name = student.get("name", "Unknown")
            self.tree.insert("", "end", values=(roll, name))

    def on_take_attendance(self):
        """Open attendance screen"""
        if not self.current_class or not self.students_list:
            messagebox.showwarning("Warning", "No students to take attendance.")
            return
        self.controller.open_attendance_screen(self.current_class, self.students_list)
