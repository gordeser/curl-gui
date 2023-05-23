import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

import subprocess
import re


class Application(tk.Tk):

    def make_window(self):
        self.title("cURL GUI")
        self.geometry("1000x500")

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
