# gui/login_screen.py
import tkinter as tk
from tkinter import messagebox
from services.auth_service import validate_lecturer


class LoginScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.show_pw = False  # Track password visibility

        # Heading
        heading = tk.Label(self, text="Lecturer Login", font=("Arial", 18, "bold"))
        heading.pack(pady=20)

        # Form container
        form = tk.Frame(self)
        form.pack(pady=10)

        # Email
        tk.Label(form, text="Email").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.email_var = tk.StringVar()
        tk.Entry(form, textvariable=self.email_var, width=40).grid(row=0, column=1, padx=5, pady=5)

        # Password
        tk.Label(form, text="Password").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.pw_var = tk.StringVar()
        self.pw_entry = tk.Entry(form, textvariable=self.pw_var, show="*", width=40)
        self.pw_entry.grid(row=1, column=1, padx=5, pady=5)

        # Show/Hide password button
        self.toggle_btn = tk.Button(form, text="Show", command=self.toggle_password, width=6)
        self.toggle_btn.grid(row=1, column=2, padx=5)

        # Login button
        tk.Button(
            self,
            text="Login",
            command=self.on_login,
            width=20,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold")
        ).pack(pady=15)

        # Message label
        self.msg = tk.Label(self, text="", fg="red", font=("Arial", 10))
        self.msg.pack()

    def toggle_password(self):
        """Toggle password visibility."""
        self.show_pw = not self.show_pw
        self.pw_entry.config(show="" if self.show_pw else "*")
        self.toggle_btn.config(text="Hide" if self.show_pw else "Show")

    def on_login(self):
        """Handle lecturer login."""
        email = self.email_var.get().strip()
        pw = self.pw_var.get().strip()

        if not email or not pw:
            self.msg.config(text="Enter email and password")
            return

        prof = validate_lecturer(email, pw)
        if prof:
            # Save lecturer info in the controller
            self.controller.lecturer = prof

            self.msg.config(text="")
            self.pw_var.set("")

            messagebox.showinfo("Login Success", f"Welcome {prof.get('name', email)}")

            # Pass full profile to dashboard
            self.controller.show_dashboard_for(prof)
        else:
            self.msg.config(text="Invalid credentials")
            messagebox.showerror("Login Failed", "Invalid email or password")
