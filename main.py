import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

import subprocess
import re


class Application(tk.Tk):

    def make_window(self):
        self.title("cURL GUI")
        self.geometry("1000x500")

    def ask_for_directory(self):
        filepath = filedialog.askdirectory()
        if filepath:
            self.input_path.delete(0, tk.END)
            self.input_path.insert(0, filepath)

    def set_positions(self):
        self.label_title.place(x=175, y=10)
        self.label_download_url.place(x=10, y=100)
        self.label_path.place(x=10, y=130)
        self.input_download.place(x=150, y=100)
        self.input_path.place(x=150, y=130)
        self.button_select_path.place(x=460, y=125)
        self.button_download.place(x=200, y=200)

    def set_binds(self):
        def on_entry_click_in():
            if self.text_input_download.get() == "http://":
                self.text_input_download.set("")

        def on_entry_click_out():
            if self.text_input_download.get() == "":
                self.text_input_download.set("http://")

        self.input_download.bind("<FocusIn>", on_entry_click_in)
        self.input_download.bind("<FocusOut>", on_entry_click_out)

    def __init__(self):
        super().__init__()

        self.make_window()

        # variables
        self.text_input_download = tk.StringVar()
        self.text_input_download.set("http://")

        # labels
        self.label_title = tk.Label(self, text="cURL GUI", font=("Arial", 20, "bold"))
        self.label_download_url = tk.Label(self, text="Download URL: ", font=("Arial", 11))
        self.label_path = tk.Label(self, text="Path: ", font=("Arial", 11))

        # entries
        self.input_download = tk.Entry(self, width=50, textvariable="self.text_input_download")
        self.input_path = tk.Entry(self, width=50)

        # buttons
        self.button_select_path = tk.Button(self, text="Choose folder", command=self.ask_for_directory)
        self.button_download = tk.Button(self, text="Download", width=10, command=self.download_file)

        # other set functions
        self.set_positions()
        self.set_binds()


if __name__ == "__main__":
    app = Application()
    app.mainloop()
