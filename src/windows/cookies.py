import tkinter as tk

from tkinter import ttk


class CookiesWindow(tk.Toplevel):

    def make_window(self):
        self.title("Set cookies")
        self.geometry("395x295")
        self.resizable(False, False)
        self.withdraw()

    def set_positions(self):
        self.label_information.place(x=10, y=10)

        self.text_cookies.place(x=4, y=60)

    def __init__(self, parent):
        super().__init__(parent)

        self.make_window()

        self.label_information = ttk.Label(
            self,
            text="Write your cookies in format cookie1=value1 \n"
                 "Divide cookies by new line",
            font=("Arial", 12)
        )

        self.text_cookies = tk.Text(self, width=48, height=14)

        self.set_positions()
