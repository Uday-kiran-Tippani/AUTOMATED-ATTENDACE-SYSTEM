# register_lecturer.py
import tkinter as tk
from tkinter import messagebox
import sys
import os
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.firebase_config import get_lecturer_ref, auth  # now we also import auth


class RegisterLecturer:
    def __init__(self, root):
        self.root = root
        self.root.title("Register New Lecturer")
        self.root.geometry("420x600")

        # ---------------- NAME ----------------
        tk.Label(root, text="Lecturer Name:").pack(pady=(5, 0))
        self.name_entry = tk.Entry(root, width=30)
        self.name_entry.pack()
        self.name_error = tk.Label(root, text="", fg="red", font=("Arial", 8))
        self.name_error.pack()

        # ---------------- MOBILE ----------------
        tk.Label(root, text="Mobile:").pack(pady=(5, 0))
        self.mobile_entry = tk.Entry(root, width=30)
        self.mobile_entry.pack()
        self.mobile_error = tk.Label(root, text="", fg="red", font=("Arial", 8))
        self.mobile_error.pack()

        # ---------------- EMAIL ----------------
        tk.Label(root, text="Email:").pack(pady=(5, 0))
        self.email_entry = tk.Entry(root, width=30)
        self.email_entry.pack()
        self.email_error = tk.Label(root, text="", fg="red", font=("Arial", 8))
        self.email_error.pack()

        # ---------------- PASSWORD ----------------
        tk.Label(root, text="Password:").pack(pady=(5, 0))
        self.password_entry = tk.Entry(root, show='*', width=30)
        self.password_entry.pack()
        self.password_error = tk.Label(root, text="", fg="red", font=("Arial", 8))
        self.password_error.pack()

        # Show/Hide password checkbox
        self.show_pass_var = tk.IntVar()
        tk.Checkbutton(root, text="Show Password", variable=self.show_pass_var,
                       command=self.toggle_password).pack()

        # ---------------- CLASSES ----------------
        tk.Label(root, text="Classes:").pack(pady=(5, 0))
        class_input_frame = tk.Frame(root)
        class_input_frame.pack(pady=5)

        self.class_entry = tk.Entry(class_input_frame, width=20)
        self.class_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(class_input_frame, text="ADD", command=self.add_class).pack(side=tk.LEFT)

        self.class_list_frame = tk.Frame(root)
        self.class_list_frame.pack(pady=10)
        self.classes = []

        tk.Button(root, text="Add Lecturer", command=self.add_lecturer).pack(pady=20)

    # ---------------- UTILITIES ----------------
    def toggle_password(self):
        if self.show_pass_var.get() == 1:
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")

    def add_class(self):
        class_name = self.class_entry.get().strip()
        if class_name and class_name not in self.classes:
            self.classes.append(class_name)
            class_frame = tk.Frame(self.class_list_frame)
            class_frame.pack(pady=2)
            tk.Label(class_frame, text=class_name).pack(side=tk.LEFT)
            tk.Button(class_frame, text="❌",
                      command=lambda f=class_frame, c=class_name: self.remove_class(f, c)).pack(side=tk.LEFT)
            self.class_entry.delete(0, tk.END)

    def remove_class(self, frame, class_name):
        frame.destroy()
        self.classes.remove(class_name)

    # ---------------- VALIDATORS ----------------
    def validate_email(self, email):
        email = email.lower()
        pattern = r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.(com|in|org|edu|net|gov)$"
        return re.match(pattern, email) is not None

    def validate_phone(self, phone):
        if not (phone.isdigit() and len(phone) == 10):
            return False
        if phone[0] not in "6789":
            return False
        if phone in ["0000000000", "1111111111", "1234567890"]:
            return False
        return True

    def validate_password(self, password):
        """Password must be strong: 8+ chars, uppercase, lowercase, number, special char"""
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        return re.match(pattern, password) is not None

    # ---------------- MAIN ACTION ----------------
    def add_lecturer(self):
        # Reset errors
        self.name_error.config(text="")
        self.mobile_error.config(text="")
        self.email_error.config(text="")
        self.password_error.config(text="")

        name = self.name_entry.get().strip()
        mobile = self.mobile_entry.get().strip()
        email = self.email_entry.get().strip().lower()
        password = self.password_entry.get().strip()

        errors = False

        if not name:
            self.name_error.config(text="Name is required")
            errors = True
        if not self.validate_phone(mobile):
            self.mobile_error.config(text="Enter a valid 10-digit mobile (6-9 start)")
            errors = True
        if not self.validate_email(email):
            self.email_error.config(text="Enter a valid email (e.g. user@gmail.com)")
            errors = True
        if not self.validate_password(password):
            self.password_error.config(
                text="Password must be 8+ chars, include A-Z, a-z, 0-9, and special char"
            )
            errors = True
        if not self.classes:
            messagebox.showerror("Error", "Add at least one class!")
            errors = True

        if errors:
            return

        ref = get_lecturer_ref()
        existing = ref.get()

        if existing:
            for key, val in existing.items():
                if val["email"].lower() == email:
                    self.email_error.config(text="Lecturer already exists with this email")
                    return

        # ✅ Step 1: Create lecturer in Firebase Authentication
        try:
            user = auth.create_user(
                email=email,
                password=password,
                display_name=name
            )
            uid = user.uid
        except Exception as e:
            messagebox.showerror("Auth Error", f"Failed to create lecturer authentication account.\n{e}")
            print(f"❌ Error creating lecturer auth: {e}")
            return

        # ✅ Step 2: Store lecturer details in Realtime Database
        email_key = email.replace(".", "_")
        ref.child(email_key).set({
            "uid": uid,
            "name": name,
            "mobile": mobile,
            "email": email,
            "classes": self.classes
        })

        # ✅ Step 3: Send success message & email
        self.send_email(email, name, mobile, password, self.classes)
        messagebox.showinfo("Success", f"Lecturer '{name}' added successfully!")
        self.root.destroy()

    # ---------------- EMAIL ----------------
    def send_email(self, to_email, name, mobile, password, classes):
        sender_email = "YOUR SENDER'S EMAIL ID"#place the email id from which gmail everyone recive the email bacically the college/universities email id
        sender_password = "YOUR GAMIL APP PASSWORD" #it's not a normal password so search for it in google and fill this carefully

        subject = "Welcome! You are successfully registered"
        body = f"""
Dear {name},

🎉 Congratulations! You are successfully registered as a lecturer in our college.

Your login details:
--------------------
Name: {name}
Mobile: {mobile}
Email: {to_email}
Password: {password}   (Please keep this safe)
Classes Assigned: {", ".join(classes)}

Regards,
College Administration
"""

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


if __name__ == "__main__":
    root = tk.Tk()
    app = RegisterLecturer(root)
    root.mainloop()
