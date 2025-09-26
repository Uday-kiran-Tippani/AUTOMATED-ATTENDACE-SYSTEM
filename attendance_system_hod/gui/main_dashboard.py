# gui/main_dashboard.py
import tkinter as tk
from tkinter import messagebox
from register_lecturer import RegisterLecturer
from update_lecturer import UpdateLecturer

class HODDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("HOD / Principal Dashboard")
        self.root.geometry("400x250")

        tk.Label(root, text="Welcome HOD / Principal", font=("Helvetica", 16)).pack(pady=20)

        # Button to open Register Lecturer window
        tk.Button(root, text="Register New Lecturer", width=25, height=2,
                  command=self.open_register).pack(pady=10)

        # Button to open Update/Delete Lecturer window
        tk.Button(root, text="Update / Remove Lecturer", width=25, height=2,
                  command=self.open_update).pack(pady=10)

        # Exit button
        tk.Button(root, text="Exit", width=15, height=2, command=root.quit).pack(pady=10)

    def open_register(self):
        register_window = tk.Toplevel(self.root)
        RegisterLecturer(register_window)

    def open_update(self):
        update_window = tk.Toplevel(self.root)
        UpdateLecturer(update_window)

if __name__ == "__main__":
    root = tk.Tk()
    app = HODDashboard(root)
    root.mainloop()
