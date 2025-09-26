import tkinter as tk
from tkinter import messagebox
import sys
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.firebase_config import get_lecturer_ref


class UpdateLecturer:
    def __init__(self, root):
        self.root = root
        self.root.title("Update Lecturer")
        self.root.geometry("450x500")

        # Dropdown to select lecturer
        tk.Label(root, text="Select Lecturer:").pack(pady=5)
        self.lecturer_var = tk.StringVar(root)
        self.lecturer_dropdown = tk.OptionMenu(root, self.lecturer_var, "")
        self.lecturer_dropdown.pack(pady=5)

        # Frame for classes
        tk.Label(root, text="Assigned Classes:").pack(pady=5)
        self.class_list_frame = tk.Frame(root)
        self.class_list_frame.pack(pady=10)

        # Add new class entry
        tk.Label(root, text="Add New Class:").pack(pady=5)
        class_add_frame = tk.Frame(root)
        class_add_frame.pack(pady=5)

        self.class_entry = tk.Entry(class_add_frame, width=25)
        self.class_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(class_add_frame, text="ADD", command=self.add_class).pack(side=tk.LEFT)

        # Buttons
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Update Lecturer", command=self.update_lecturer).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Delete Lecturer", command=self.delete_lecturer).pack(side=tk.LEFT, padx=10)

        # Internal state
        self.lecturers = {}
        self.classes = []

        # Load lecturers from Firebase
        self.load_lecturers()

    def load_lecturers(self):
        ref = get_lecturer_ref()
        data = ref.get()

        if not data:
            messagebox.showinfo("Info", "No lecturers found.")
            return

        self.lecturers = data
        menu = self.lecturer_dropdown["menu"]
        menu.delete(0, "end")

        for key, val in data.items():
            menu.add_command(label=val["name"], command=lambda v=key: self.select_lecturer(v))

    def select_lecturer(self, lecturer_id):
        self.lecturer_var.set(self.lecturers[lecturer_id]["name"])
        self.current_lecturer_id = lecturer_id
        self.current_lecturer_email = self.lecturers[lecturer_id].get("email", "")
        self.classes = self.lecturers[lecturer_id].get("classes", [])
        self.display_classes()

    def display_classes(self):
        for widget in self.class_list_frame.winfo_children():
            widget.destroy()

        for c in self.classes:
            class_frame = tk.Frame(self.class_list_frame)
            class_frame.pack(pady=2)
            tk.Label(class_frame, text=c).pack(side=tk.LEFT)
            tk.Button(class_frame, text="❌", command=lambda f=class_frame, cc=c: self.remove_class(f, cc)).pack(side=tk.LEFT)

    def add_class(self):
        class_name = self.class_entry.get().strip()
        if class_name and class_name not in self.classes:
            self.classes.append(class_name)
            self.display_classes()
            self.class_entry.delete(0, tk.END)

    def remove_class(self, frame, class_name):
        frame.destroy()
        self.classes.remove(class_name)

    def send_email(self, to_email, subject, body):
        sender_email = "yoursendersemailid@gmail.com"  # replace with your Gmail
        sender_password = "laex oefz irwu pata"  # replace with Gmail App Password

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
            server.quit()
            print(f"✅ Email sent to {to_email}")
        except Exception as e:
            print(f"❌ Failed to send email: {e}")

    def update_lecturer(self):
        if not hasattr(self, "current_lecturer_id"):
            messagebox.showerror("Error", "Please select a lecturer first.")
            return

        ref = get_lecturer_ref().child(self.current_lecturer_id)
        ref.update({"classes": self.classes})
        messagebox.showinfo("Success", "Lecturer updated successfully!")

        # Send email notification
        if self.current_lecturer_email:
            subject = "Lecturer Record Updated"
            body = f"Dear {self.lecturer_var.get()},\n\nYour assigned classes have been updated to:\n{', '.join(self.classes)}\n\nRegards,\nCollege Administration"
            self.send_email(self.current_lecturer_email, subject, body)

    def delete_lecturer(self):
        if not hasattr(self, "current_lecturer_id"):
            messagebox.showerror("Error", "Please select a lecturer first.")
            return

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {self.lecturer_var.get()}?")
        if confirm:
            ref = get_lecturer_ref().child(self.current_lecturer_id)
            ref.delete()
            messagebox.showinfo("Deleted", "Lecturer deleted successfully!")

            # Send email notification
            if self.current_lecturer_email:
                subject = "Lecturer Record Deleted"
                body = f"Dear {self.lecturer_var.get()},\n\nYour record has been deleted from the college database\nPlease Contact the Admin/Department Head For Details.\n\nRegards,\nCollege Administration"
                self.send_email(self.current_lecturer_email, subject, body)

            self.load_lecturers()
