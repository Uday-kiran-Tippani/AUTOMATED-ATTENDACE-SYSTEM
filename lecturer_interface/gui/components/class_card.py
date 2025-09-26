# gui/components/class_card.py
import tkinter as tk
from tkinter import Frame, Label
from utils.colors import get_class_color

class ClassCard(Frame):
    def __init__(self, parent, class_name: str, index: int, on_click=None):
        """
        ClassCard - A colored rectangular card representing a class.

        Args:
            parent: Tkinter parent widget.
            class_name (str): Name of the class (e.g., "MCA I").
            index (int): Index of the card (for choosing gradient color).
            on_click (function): Callback when card is clicked.
        """
        super().__init__(parent, bd=2, relief="raised", cursor="hand2")

        # Pick gradient colors
        start_color, end_color = get_class_color(index)

        # Background (we fake gradient with two halves for Tkinter simplicity)
        self.top_frame = Frame(self, bg=start_color, height=40)
        self.top_frame.pack(fill="x", side="top")

        self.bottom_frame = Frame(self, bg=end_color, height=40)
        self.bottom_frame.pack(fill="x", side="top")

        # Class name label
        self.label = Label(
            self,
            text=class_name,
            font=("Arial", 14, "bold"),
            fg="white",
            bg=end_color,
            padx=10,
            pady=10
        )
        self.label.place(relx=0.5, rely=0.5, anchor="center")

        # Click binding
        if on_click:
            self.bind("<Button-1>", lambda e: on_click(class_name))
            self.top_frame.bind("<Button-1>", lambda e: on_click(class_name))
            self.bottom_frame.bind("<Button-1>", lambda e: on_click(class_name))
            self.label.bind("<Button-1>", lambda e: on_click(class_name))
