# gui/attendance_screen.py
import tkinter as tk
from tkinter import ttk, messagebox
from threading import Lock
from PIL import Image, ImageTk
import numpy as np
import cv2
from services.attendance_service import mark_attendance
from services.student_service import get_students_for_class
from services.face_recognition_service import CameraRecognizer


class AttendanceScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # --- Topbar ---
        topbar = tk.Frame(self, height=50, bg="#f8f8f8")
        topbar.pack(fill="x")
        tk.Button(topbar, text="← Back", command=self.on_back).pack(side="left", padx=8)
        self.class_label = tk.Label(topbar, text="", font=("Arial", 14))
        self.class_label.pack(side="left", padx=12)

        # --- Layout: left = student table, right = camera feed ---
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        # Left frame: student table
        left = tk.Frame(container)
        left.pack(side="left", fill="both", expand=False, padx=8, pady=8)
        cols = ("roll", "name", "status")
        self.tree = ttk.Treeview(left, columns=cols, show="headings", height=20)
        for col in cols:
            self.tree.heading(col, text=col.title())
            self.tree.column(col, width=140, anchor="center")
        self.tree.pack(fill="both", expand=True)

        # Quick-select buttons
        btn_frame = tk.Frame(left)
        btn_frame.pack(fill="x", pady=6)
        tk.Button(btn_frame, text="Mark Selected Present", command=self.mark_selected_present).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Mark Selected Absent", command=self.mark_selected_absent).pack(side="left", padx=4)

        # Mark Attendance button
        self.mark_btn = tk.Button(left, text="Mark Attendance (Save to Sheet)", command=self.on_mark_attendance, state="disabled")
        self.mark_btn.pack(fill="x", pady=6)

        # Right frame: camera feed
        right = tk.Frame(container, bg="#000")
        right.pack(side="right", fill="both", expand=True, padx=8, pady=8)
        self.cam_label = tk.Label(right)
        self.cam_label.pack(expand=True, fill="both")

        # Bottom: absent list
        bottom = tk.Frame(self, bg="#fff0f0", height=40)
        bottom.pack(fill="x", side="bottom")
        self.absent_label = tk.Label(bottom, text="Absent: ", fg="red", bg="#fff0f0", anchor="w")
        self.absent_label.pack(fill="x", padx=8, pady=6)

        # Internal state
        self.class_name = None
        self.lecturer_email = None
        self.students_list = []

        self.known_encodings = []
        self.known_rolls = []
        self.known_names = []
        self.recognized = set()
        self.table_lock = Lock()

        self.recognizer = None  # CameraRecognizer instance

    # ----------------- Load students & start recognition -----------------
    def load(self, class_name, students_list=None, lecturer_email=""):
        self.class_name = class_name
        self.lecturer_email = lecturer_email
        self.class_label.config(text=f"Class: {class_name}")

        # Fetch students & face encodings from DB
        try:
            fetched = get_students_for_class(class_name)
            self.students_list = fetched or students_list or []
        except Exception as e:
            print(f"[ERROR] Failed to fetch students for {class_name}: {e}")
            self.students_list = students_list or []

        print(f"[INFO] Loaded {len(self.students_list)} students for class {class_name}")

        # Build known encodings
        self.known_encodings = []
        self.known_rolls = []
        self.known_names = []
        for s in self.students_list:
            roll = str(s.get("roll_number") or "")
            name = s.get("name", "")
            enc = s.get("face_encoding")
            if enc is not None:
                self.known_encodings.append(np.asarray(enc, dtype=np.float64))
                self.known_rolls.append(roll)
                self.known_names.append(name)

        print(f"[INFO] Prepared {len(self.known_encodings)} encodings for recognition")

        # populate table
        with self.table_lock:
            for i in self.tree.get_children():
                self.tree.delete(i)
            for s in self.students_list:
                roll = str(s.get("roll_number") or "")
                name = s.get("name", "Unknown")
                self.tree.insert("", "end", iid=roll, values=(roll, name, "Absent"))

        self.recognized.clear()
        self.update_absent_label()

        if self.students_list:
            self.mark_btn.config(state="normal")
        else:
            self.mark_btn.config(state="disabled")

        # Start CameraRecognizer
        self.recognizer = CameraRecognizer(
            known_encodings=self.known_encodings,
            known_rolls=self.known_rolls,
            known_names=self.known_names,
            tolerance=0.5
        )
        print("[INFO] Starting face recognizer...")
        self.recognizer.start()
        self.after(50, self._poll_recognizer_queue)

    # ----------------- Poll recognizer queue -----------------
    def _poll_recognizer_queue(self):
        if self.recognizer:
            while not self.recognizer.queue.empty():
                ev = self.recognizer.queue.get()
                if "error" in ev:
                    messagebox.showerror("Recognizer Error", ev["error"])
                    print(f"[ERROR] Recognizer error: {ev['error']}")
                    self.on_back()
                    return
                roll = ev.get("roll")
                name = ev.get("name")
                if roll and name:
                    self._handle_recognition(roll, name)

            # Update camera frame
            if self.recognizer.capture:
                ret, frame = self.recognizer.capture.read()
                if ret:
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil = Image.fromarray(rgb)
                    imgtk = ImageTk.PhotoImage(pil)
                    self.cam_label.imgtk = imgtk
                    self.cam_label.config(image=imgtk)

        self.after(30, self._poll_recognizer_queue)

    # ----------------- Handle recognition -----------------
    def _handle_recognition(self, roll, name):
        if not roll or roll in self.recognized:
            return
        self.recognized.add(roll)
        with self.table_lock:
            if self.tree.exists(roll):
                vals = list(self.tree.item(roll, "values"))
                vals[2] = "Present"
                self.tree.item(roll, values=vals)
        self.update_absent_label()

    # ----------------- Update absent label -----------------
    def update_absent_label(self):
        all_rolls = [str(s.get("roll_number") or "") for s in self.students_list]
        absent = [r for r in all_rolls if r not in self.recognized]
        text = "Absent: " + (", ".join(absent) if absent else "None")
        self.absent_label.config(text=text)

    # ----------------- Manual mark present/absent -----------------
    def mark_selected_present(self):
        sel = self.tree.selection()
        for iid in sel:
            vals = list(self.tree.item(iid, "values"))
            vals[2] = "Present"
            self.tree.item(iid, values=vals)
            self.recognized.add(str(iid))
        self.update_absent_label()

    def mark_selected_absent(self):
        sel = self.tree.selection()
        for iid in sel:
            vals = list(self.tree.item(iid, "values"))
            vals[2] = "Absent"
            self.tree.item(iid, values=vals)
            self.recognized.discard(str(iid))
        self.update_absent_label()

    # ----------------- Mark attendance -----------------
    def on_mark_attendance(self):
        try:
            present = list(self.recognized)
            students_master = [
                {"roll": str(s.get("roll_number") or ""), "name": s.get("name", "")}
                for s in self.students_list
            ]

            print(f"[SAVE] Marking attendance for {len(present)} students present...")

            # Call attendance service (saves to Google Sheet + sends email)
            mark_attendance(self.lecturer_email, self.class_name, present, students_master)

            messagebox.showinfo("Success", "Attendance marked successfully and email sent!")
            self.mark_btn.config(state="disabled")

        except Exception as e:
            print(f"[ERROR] Failed to mark attendance: {e}")
            messagebox.showerror("Error", f"Failed to mark attendance:\n{e}")

    # ----------------- Back navigation -----------------
    def on_back(self):
        if self.recognizer:
            print("[INFO] Stopping recognizer...")
            self.recognizer.stop()
            self.recognizer = None
        self.controller.show_frame("class")
