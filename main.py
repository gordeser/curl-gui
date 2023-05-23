import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

import subprocess
import re
import platform
import os


class Application(tk.Tk):

    def make_window(self):
        self.title("cURL GUI")
        self.geometry("1000x500")

    @staticmethod
    def get_init_dir():
        system_name = platform.system()
        if system_name == "Windows":
            return os.path.expandvars("%USERPROFILE%")
        elif system_name == "Linux" or system_name == "macOS" or system_name == "Darwin":
            return os.path.expanduser("~")
        else:
            return ""

    def ask_for_directory(self):
        init_dir = self.get_init_dir()
        filepath = filedialog.askdirectory(initialdir=init_dir, title="Choose directory to save file")
        if filepath:
            self.input_path.delete(0, tk.END)
            self.input_path.insert(0, filepath)

    def ask_for_file(self):
        init_dir = self.get_init_dir()
        filepath = filedialog.askopenfilename(initialdir=init_dir, title="Choose file to upload")
        print(type(filepath))
        if filepath:
            self.input_upload.delete(0, tk.END)
            self.input_upload.insert(0, filepath)

    def download_file(self):
        path_to_save = self.input_path.get()
        link_download = self.input_download.get()
        selected_option = self.combobox_speedlimit.get()
        postfix = ''

        if selected_option == 'B/S':
            postfix = ''
        elif selected_option == 'kB/S':
            postfix = 'K'
        elif selected_option == 'MB/S':
            postfix = 'M'
        elif selected_option == 'GB/S':
            postfix = 'G'
        else:
            print("some error idk")

        if not self.check_speedlimit():
            print("incorrect speedlimit")  # todo show error
            return False

        result = re.search(r"/([^/]+)/?$", link_download)
        if result:
            file_name = result.group(1)
            command = ['curl', '--limit-rate', f"{str(self.speedlimit)}{postfix}", '-o', f"{path_to_save}/{file_name}", link_download]
            try:
                subprocess.run(command, check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as e:
                print(e)  # todo for every(?) exit code make window with error https://everything.curl.dev/usingcurl/returns
        else:
            # todo make error with invalid link
            pass

    def upload_file(self):
        file = self.input_upload.get()
        path_to_upload = self.input_download.get()
        selected_option = self.combobox_speedlimit.get()
        postfix = ''

        if selected_option == 'B/S':
            postfix = ''
        elif selected_option == 'kB/S':
            postfix = 'K'
        elif selected_option == 'MB/S':
            postfix = 'M'
        elif selected_option == 'GB/S':
            postfix = 'G'
        else:
            print("some error idk")

        if not self.check_speedlimit():
            print("incorrect speedlimit")  # todo show error
            return False

        command = ['curl', '--limit-rate', f"{str(self.speedlimit)}{postfix}", '-F', f'file=@{file}', path_to_upload]
        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print(e)  # todo for every(?) exit code make window with error

    def set_positions(self):
        self.label_title.place(x=175, y=10)
        self.label_download_url.place(x=10, y=100)
        self.label_path_to_save.place(x=10, y=130)
        self.label_path_to_upload.place(x=10, y=160)
        self.input_download.place(x=150, y=100)
        self.input_path.place(x=150, y=130)
        self.input_upload.place(x=150, y=160)
        self.button_select_path.place(x=460, y=125)
        self.button_download.place(x=550, y=125)
        self.button_select_file.place(x=460, y=155)
        self.button_upload.place(x=550, y=155)

    def set_binds(self):
        def on_entry_click_in(event):
            if self.text_input_download.get() == "http://":
                self.text_input_download.set("")

        def on_entry_click_out(event):
            if self.text_input_download.get() == "":
                self.text_input_download.set("http://")

        self.input_download.bind("<FocusIn>", on_entry_click_in)
        self.input_download.bind("<FocusOut>", on_entry_click_out)

    def __init__(self):
        super().__init__()

        self.make_window()

        # variables
        self.text_input_download = tk.StringVar()
        self.speedlimit = 0

        # labels
        self.label_title = tk.Label(self, text="cURL GUI", font=("Arial", 20, "bold"))
        self.label_download_url = tk.Label(self, text="Download URL: ", font=("Arial", 11))
        self.label_path_to_save = tk.Label(self, text="Path to save file: ", font=("Arial", 11))
        self.label_path_to_upload = tk.Label(self, text="Path to upload file: ", font=("Arial", 11))
        self.label_speedlimit = tk.Label(self, text="Speed limit", font=("Arial", 11))

        # entries
        self.input_download = tk.Entry(self, width=50, textvariable=self.text_input_download)
        self.input_path = tk.Entry(self, width=50)
        self.input_upload = tk.Entry(self, width=50)
        self.input_speedlimit = tk.Entry(self, width=5)

        # buttons
        self.button_select_path = tk.Button(self, text="Choose folder", command=self.ask_for_directory)
        self.button_download = tk.Button(self, text="Download file", command=self.download_file)
        self.button_select_file = tk.Button(self, text="Choose file", command=self.ask_for_file)
        self.button_upload = tk.Button(self, text="Upload file", command=self.upload_file)

        # combo boxes
        self.combobox_speedlimit = ttk.Combobox(self, values=['B/S', 'kB/S', 'MB/S', 'GB/S'], width=5, state="readonly")

        # other set functions
        self.set_positions()
        self.set_binds()
        self.set_currents()


if __name__ == "__main__":
    app = Application()
    app.mainloop()
