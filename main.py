import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

import subprocess


class Application(tk.Tk):

    def make_window(self):
        self.title("cURL GUI")
        self.geometry("1000x500")

    def __init__(self):
        super().__init__()

        self.make_window()

        self.label_title = tk.Label(self, text="cURL GUI", font=("Arial", 20, "bold"))
        self.label_title.place(x=175, y=10)

        self.label_download = tk.Label(self, text="Download URL: ", font=("Arial", 11))
        self.label_download.place(x=10, y=100)

        self.input_download = tk.Entry(self, width=50)
        self.input_download.place(x=150, y=100)

        self.button_download = tk.Button(self, text="Download", width=10)
        self.button_download.place(x=200, y=200)



if __name__ == "__main__":
    app = Application()
    app.mainloop()
