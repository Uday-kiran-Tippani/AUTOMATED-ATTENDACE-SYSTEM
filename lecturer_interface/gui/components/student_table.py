# gui/components/student_table.py
import tkinter as tk
from tkinter import ttk

class StudentTable(ttk.Frame):
    def __init__(self, parent, columns=("Roll No", "Name", "Status")):
        super().__init__(parent)

        # Scrollbars
        self.v_scroll = ttk.Scrollbar(self, orient="vertical")
        self.h_scroll = ttk.Scrollbar(self, orient="horizontal")

        # Treeview
        self.tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            yscrollcommand=self.v_scroll.set,
            xscrollcommand=self.h_scroll.set,
            height=15
        )

        # Attach scrollbars
        self.v_scroll.config(command=self.tree.yview)
        self.h_scroll.config(command=self.tree.xview)

        self.v_scroll.pack(side="right", fill="y")
        self.h_scroll.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)

        # Define columns
        for col in columns:
            self.tree.heading(col, text=col, anchor="center")
            self.tree.column(col, anchor="center", width=150)

    def load_students(self, students: list):
        """
        Load students into the table.
        Args:
            students (list): List of dicts with keys matching columns.
        """
        self.clear()
        for student in students:
            values = [student.get("roll_no", ""), student.get("name", ""), student.get("status", "")]
            self.tree.insert("", "end", values=values)

    def update_status(self, roll_no: str, status: str):
        """Update a student’s status (e.g., Present/Absent)."""
        for item in self.tree.get_children():
            vals = self.tree.item(item, "values")
            if vals[0] == roll_no:
                self.tree.item(item, values=(vals[0], vals[1], status))
                break

    def clear(self):
        """Clear all rows from the table."""
        for item in self.tree.get_children():
            self.tree.delete(item)
