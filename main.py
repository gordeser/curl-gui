import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

import subprocess
import re
import platform
import os
import datetime


class Application(tk.Tk):

    @staticmethod
    def show_error(message):
        messagebox.showerror("Error", message)

    @staticmethod
    def get_init_dir():
        system_name = platform.system()
        if system_name == "Windows":
            return os.path.expandvars("%USERPROFILE%")
        elif system_name == "Linux" or system_name == "macOS" or system_name == "Darwin":
            return os.path.expanduser("~")
        else:
            return ""

    @staticmethod
    def create_logs_directory():
        if not os.path.exists("logs"):
            os.makedirs("logs")

    def make_window(self):
        self.title("cURL GUI")
        self.geometry("1000x500")
        self.resizable(False, False)

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

    def check_speedlimit(self):
        if not self.input_speedlimit.get():
            self.speedlimit = 0
            return True

        try:
            self.speedlimit = int(self.input_speedlimit.get())
            if self.speedlimit < 0:
                self.show_error("Speed limit value must be 0 or greater")
                return False
        except ValueError:
            self.show_error("Speed limit value must be a number")
            return False
        return True

    def get_postfix(self):
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
            self.show_error("Incorrect speed limit option")
        return postfix

    def output_logs(self, process):
        while True:
            line = process.stdout.readline()
            if not line:
                break
            self.window_debug.text_logs.config(state=tk.NORMAL)
            self.window_debug.text_logs.insert(tk.END, line)
            self.window_debug.text_logs.see(tk.END)
            self.window_debug.text_logs.config(state=tk.DISABLED)
            self.window_debug.text_logs.update()

    def execute(self, command):
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        thread = threading.Thread(target=self.output_logs, args=[process])
        thread.start()

    def download_file(self):
        path_to_save = self.input_path.get()
        link_download = self.input_download.get()
        postfix = self.get_postfix()

        if not self.check_speedlimit():
            return False

        result = re.search(r"/([^/]+)/?$", link_download)
        if result:
            file_name = result.group(1)
            command = f"curl {'--verbose' * int(self.verbose.get())} --limit-rate {str(self.speedlimit)}{postfix} -o {path_to_save}/{file_name} {link_download}"
            try:
                self.execute(command)
            except subprocess.CalledProcessError as e:
                # todo for every(?) exit code make window with error https://everything.curl.dev/usingcurl/returns
                print(e)
        else:
            self.show_error("Invalid URL")

    def upload_file(self):
        file = self.input_upload.get()
        path_to_upload = self.input_download.get()
        postfix = self.get_postfix()

        if not self.check_speedlimit():
            return False

        command = f"curl {'--verbose' * int(self.verbose.get())} --limit-rate {str(self.speedlimit)}{postfix} -F file=@{file} {path_to_upload}"
        try:
            self.execute(command)
        except subprocess.CalledProcessError as e:
            print(e)  # todo for every(?) exit code make window with error

    def export_debug(self):
        self.create_logs_directory()
        today = datetime.datetime.today()
        formatted_date = today.strftime("%Y-%m-%d_%H-%M-%S")
        with open(f"logs/log_{formatted_date}.txt", "w") as f:
            f.write(self.window_debug.text_logs.get("1.0", "end-1c"))

    def debug_mode(self):
        def on_close():
            self.debug_open.set(False)
            self.button_debug.configure(state="active")
            self.window_debug.withdraw()

        if not self.debug_open.get():
            self.window_debug.deiconify()
            self.debug_open.set(True)
            self.button_debug.configure(state="disabled")
            self.window_debug.protocol("WM_DELETE_WINDOW", on_close)

    def set_proxy(self):
        def on_close():
            self.window_proxy.withdraw()
            self.window_proxy.grab_release()

        self.window_proxy.deiconify()
        self.window_proxy.grab_set()
        self.window_proxy.protocol("WM_DELETE_WINDOW", on_close)

    def set_positions(self):
        self.label_title.place(x=175, y=10)
        self.label_download_url.place(x=10, y=100)
        self.label_path_to_save.place(x=10, y=130)
        self.label_path_to_upload.place(x=10, y=160)
        self.label_speedlimit.place(x=500, y=75)

        self.input_download.place(x=150, y=100)
        self.input_path.place(x=150, y=130)
        self.input_upload.place(x=150, y=160)
        self.input_speedlimit.place(x=500, y=100)

        self.button_select_path.place(x=460, y=125)
        self.button_download.place(x=550, y=125)
        self.button_select_file.place(x=460, y=155)
        self.button_upload.place(x=550, y=155)
        self.button_debug.place(x=350, y=250)
        self.button_proxy.place(x=450, y=250)

        self.combobox_speedlimit.place(x=550, y=100)

    def set_binds(self):
        def on_entry_click_in(event):
            if self.text_input_download.get() == "http://":
                self.text_input_download.set("")

        def on_entry_click_out(event):
            if self.text_input_download.get() == "":
                self.text_input_download.set("http://")

        self.input_download.bind("<FocusIn>", on_entry_click_in)
        self.input_download.bind("<FocusOut>", on_entry_click_out)

    def set_currents(self):
        self.combobox_speedlimit.current(0)
        self.text_input_download.set("http://")
        self.debug_open.set(False)
        self.verbose.set(False)

    def __init__(self):
        super().__init__()

        self.make_window()

        # variables
        self.text_input_download = tk.StringVar()
        self.debug_open = tk.BooleanVar()
        self.verbose = tk.BooleanVar()
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
        self.button_debug = tk.Button(self, text="Debug mode", command=self.debug_mode)
        self.button_proxy = tk.Button(self, text="Set proxy", command=self.set_proxy)

        # combo boxes
        self.combobox_speedlimit = ttk.Combobox(self, values=['B/S', 'kB/S', 'MB/S', 'GB/S'], width=5, state="readonly")

        # windows
        self.window_debug = DebugWindow(self)
        self.window_proxy = ProxyWindow(self)

        # other set functions
        self.set_positions()
        self.set_binds()
        self.set_currents()


class DebugWindow(tk.Toplevel):

    def make_window(self):
        self.title("Debug mode")
        self.geometry("805x500")
        self.resizable(False, False)
        self.withdraw()

    def set_positions(self):
        self.checkbutton_verbose.place(x=20, y=460)
        self.button_export_debug.place(x=650, y=460)
        self.button_clear_logs.place(x=350, y=460)
        self.text_logs.place(x=0, y=0)

    def clear_logs(self):
        self.text_logs.config(state=tk.NORMAL)
        self.text_logs.delete("1.0", tk.END)
        self.text_logs.config(state=tk.DISABLED)

    def __init__(self, parent):
        super().__init__(parent)
        self.make_window()

        self.checkbutton_verbose = ttk.Checkbutton(self, text="Enable verbose mode", variable=parent.verbose)

        self.button_export_debug = tk.Button(self, text="Export logs to file", command=parent.export_debug)
        self.button_clear_logs = tk.Button(self, text="Clear logs", command=self.clear_logs)

        self.text_logs = tk.Text(self, state="disabled", width=100, height=25)

        self.set_positions()


class ProxyWindow(tk.Toplevel):
    def make_window(self):
        self.title("Set Proxy")
        self.geometry("300x175")
        self.resizable(False, False)
        self.withdraw()

    def set_positions(self):
        self.label_protocol.place(x=10, y=10)
        self.label_hostname.place(x=10, y=40)
        self.label_port.place(x=10, y=70)
        self.label_username.place(x=10, y=100)
        self.label_password.place(x=10, y=130)

        self.input_hostname.place(x=100, y=40)
        self.input_port.place(x=100, y=70)
        self.input_username.place(x=100, y=100)
        self.input_password.place(x=100, y=130)

        self.combobox_protocol.place(x=100, y=10)

    def set_currents(self):
        self.combobox_protocol.current(0)

    def __init__(self, parent):
        super().__init__(parent)

        self.make_window()

        self.label_protocol = tk.Label(self, text="Protocol")
        self.label_hostname = tk.Label(self, text="Hostname")
        self.label_port = tk.Label(self, text="Port")
        self.label_username = tk.Label(self, text="Username")
        self.label_password = tk.Label(self, text="Password")

        self.input_hostname = tk.Entry(self, width=30)
        self.input_port = tk.Entry(self, width=30)
        self.input_username = tk.Entry(self, width=30)
        self.input_password = tk.Entry(self, width=30)

        self.combobox_protocol = ttk.Combobox(self, values=['HTTP', 'SOCKS5'], width=10, state="readonly")

        self.set_positions()
        self.set_currents()


if __name__ == "__main__":
    app = Application()
    app.mainloop()
