import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

import threading
import subprocess
import re
import datetime

from src.utils import get_init_dir
from src.utils import create_logs_directory

from src.windows.proxy import ProxyWindow
from src.windows.debug import DebugWindow
from src.windows.cookies import CookiesWindow

from src.constants import *


class Application(tk.Tk):

    @staticmethod
    def show_error(message):
        messagebox.showerror("Error", message)

    @staticmethod
    def show_info(message):
        messagebox.showinfo("Information", message)

    def make_window(self):
        self.title("cURL GUI")
        self.geometry("750x460")
        self.resizable(False, False)

    def ask_for_directory(self):
        init_dir = get_init_dir()
        filepath = filedialog.askdirectory(
            initialdir=init_dir,
            title="Choose directory to save file"
        )
        if filepath:
            self.input_path.delete(0, tk.END)
            self.input_path.insert(0, filepath)

    def ask_for_file(self):
        init_dir = get_init_dir()
        filepath = filedialog.askopenfilename(
            initialdir=init_dir,
            title="Choose file to upload"
        )
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
            return False
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
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        thread = threading.Thread(target=self.output_logs, args=[process])
        thread.start()
        process.wait()
        return process.returncode

    def get_proxy(self):
        proxy_command = ""

        if self.proxy.get():
            selected_protocol = self.window_proxy.combobox_protocol.get()
            if selected_protocol == "HTTP":
                protocol = "http"
            elif selected_protocol == "HTTPS":
                protocol = "https"
            elif selected_protocol == "SOCKS4":
                protocol = "socks4"
            elif selected_protocol == "SOCKS5":
                protocol = "socks5"
            else:
                self.show_error("Unknown proxy protocol")
                return False

            hostname = self.window_proxy.input_hostname.get().replace(" ", "")
            port = self.window_proxy.input_port.get().replace(" ", "")
            username = self.window_proxy.input_username.get().strip()
            password = self.window_proxy.input_password.get().strip()

            if not hostname or not port:
                self.show_error("Both hostname and port in proxy are required")
                return False

            proxy_command += f"--proxy {protocol}://{hostname}:{port} "
            proxy_command += f"--proxy-user \"{username}:{password}\""
            return proxy_command
        return " "

    def get_useragent(self):
        selected_useragent = self.combobox_useragent.get()
        if selected_useragent == "Custom":
            useragent = self.input_customuseragent.get().strip()
            if not useragent:
                self.show_error("User-agent is empty")
                return False
        else:
            return f"-A \"{self.useragents[selected_useragent]}\""

        if useragent:
            return f"-A \"{useragent}\""
        else:
            self.show_error("Unknown user-agent")
            return False

    def get_httpbasicauth(self):
        username = self.input_username.get().strip()
        password = self.input_password.get().strip()

        if not username and not password:
            return ""

        return f"--user \"{username}:{password}\""

    def get_cookies(self):
        cookies = self.window_cookies.text_cookies.get("1.0", tk.END)
        cookies = ";".join(cookies.split("\n")[:-1])
        return f"--cookie \"{cookies}\"" if len(cookies) >= 1 else ""

    def download_file(self):
        link_download = self.text_input_download.get().strip()
        if link_download == "http://":
            self.show_error("Download URL is empty")
            return False

        path_to_save = self.input_path.get().strip()
        if not path_to_save:
            self.show_error("Path to save file is empty")
            return False

        postfix = self.get_postfix()

        proxy_command = self.get_proxy()
        if not proxy_command:
            return False

        useragent = self.get_useragent()
        if not useragent:
            return False

        httpbasicauth = self.get_httpbasicauth()
        cookies = self.get_cookies()
        verbose = '--verbose' * int(self.verbose.get())

        if not self.check_speedlimit():
            return False

        result = re.search(r"/([^/]+)/?$", link_download)

        if result:
            file_name = result.group(1)
        else:
            file_name = link_download.replace("<>:\"/\\|?*", "")

        command = f"curl " \
                  f"{cookies} " \
                  f"{httpbasicauth} " \
                  f"{useragent} " \
                  f"{proxy_command} " \
                  f"{verbose} " \
                  f"--limit-rate {str(self.speedlimit)}{postfix} " \
                  f"-o {path_to_save}/{file_name} " \
                  f"-L " \
                  f"{link_download}".split()
        returncode = self.execute(command)
        message = self.errors[returncode]
        if message:
            self.show_error(message)
        else:
            self.show_info("File is downloaded successfully")

    def upload_file(self):
        path_to_upload = self.input_download.get().strip()
        if path_to_upload == "http://":
            self.show_error("Download URL is empty")
            return False

        file = self.input_upload.get().strip()
        if not file:
            self.show_error("Path to upload file is empty")
            return False

        postfix = self.get_postfix()

        proxy_command = self.get_proxy()
        if not proxy_command:
            return False

        useragent = self.get_useragent()
        if not useragent:
            return False

        httpbasicauth = self.get_httpbasicauth()
        cookies = self.get_cookies()
        verbose = '--verbose' * int(self.verbose.get())

        if not self.check_speedlimit():
            return False

        command = f"curl " \
                  f"{cookies} " \
                  f"{httpbasicauth} " \
                  f"{useragent} " \
                  f"{proxy_command} " \
                  f"{verbose} " \
                  f"--limit-rate {str(self.speedlimit)}{postfix} " \
                  f"-F file=@{file} " \
                  f"-L " \
                  f"{path_to_upload}".split()
        returncode = self.execute(command)
        message = self.errors[returncode]
        if message:
            self.show_error(message)
        else:
            self.show_info("File is downloaded successfully")

    def export_debug(self):
        create_logs_directory()
        today = datetime.datetime.today()
        formatted_date = today.strftime("%Y-%m-%d_%H-%M-%S")
        with open(f"../logs/log_{formatted_date}.txt", "w") as f:
            f.write(self.window_debug.text_logs.get("1.0", "end-1c"))
            self.show_info("Logs are exported successfully")

    def debug_mode(self):
        def on_close():
            self.debug_open.set(False)
            self.button_debug.configure(state="active")
            self.window_debug.withdraw()

        if not self.debug_open.get():
            self.window_debug.deiconify()
            self.debug_open.set(True)
            self.button_debug.configure(state=tk.DISABLED)
            self.window_debug.protocol("WM_DELETE_WINDOW", on_close)

    def set_proxy(self):
        def on_close():
            self.window_proxy.withdraw()
            self.window_proxy.grab_release()
            self.show_info("Proxy is set successfully")

        self.window_proxy.deiconify()
        self.window_proxy.grab_set()
        self.window_proxy.protocol("WM_DELETE_WINDOW", on_close)

    def set_cookies(self):
        def on_close():
            self.window_cookies.withdraw()
            self.window_cookies.grab_release()
            self.show_info("Cookies are set successfully")

        self.window_cookies.deiconify()
        self.window_cookies.grab_set()
        self.window_cookies.protocol("WM_DELETE_WINDOW", on_close)

    def set_proxy_button(self):
        if self.proxy.get():
            self.button_proxy.configure(state=tk.NORMAL)
        else:
            self.button_proxy.configure(state=tk.DISABLED)

    def set_positions(self):
        self.label_title.place(x=250, y=10)
        self.label_download_url.place(x=57, y=80)
        self.label_path_to_save.place(x=22, y=130)
        self.label_path_to_upload.place(x=10, y=160)
        self.label_speedlimit.place(x=300, y=340)
        self.label_useragent.place(x=40, y=260)
        self.label_httpbasicauth.place(x=40, y=340)
        self.label_username.place(x=40, y=370)
        self.label_password.place(x=40, y=400)

        self.input_download.place(x=140, y=80)
        self.input_path.place(x=140, y=130)
        self.input_upload.place(x=140, y=160)
        self.input_speedlimit.place(x=320, y=370)
        self.input_username.place(x=130, y=370)
        self.input_password.place(x=130, y=400)
        self.input_customuseragent.place(x=350, y=290)

        self.button_select_path.place(x=460, y=125)
        self.button_download.place(x=600, y=125)
        self.button_select_file.place(x=460, y=155)
        self.button_upload.place(x=600, y=155)
        self.button_debug.place(x=250, y=210)
        self.button_proxy.place(x=135, y=210)
        self.button_cookies.place(x=370, y=210)

        self.combobox_speedlimit.place(x=350, y=370)
        self.combobox_useragent.place(x=40, y=290)

        self.checkbutton_enable_proxy.place(x=40, y=210)

    def set_binds(self):
        def on_entry_click_in(_):
            if self.text_input_download.get() == "http://":
                self.text_input_download.set("")

        def on_entry_click_out(_):
            if self.text_input_download.get() == "":
                self.text_input_download.set("http://")

        def on_custom(_):
            selected_option = self.combobox_useragent.get()
            if selected_option == "Custom":
                self.input_customuseragent.configure(state=tk.NORMAL)
            else:
                self.input_customuseragent.configure(state=tk.DISABLED)

        self.input_download.bind("<FocusIn>", on_entry_click_in)
        self.input_download.bind("<FocusOut>", on_entry_click_out)
        self.combobox_useragent.bind("<<ComboboxSelected>>", on_custom)

    def set_currents(self):
        self.combobox_speedlimit.current(0)
        self.combobox_useragent.current(0)
        self.text_input_download.set("http://")
        self.debug_open.set(False)
        self.verbose.set(False)
        self.proxy.set(False)
        self.input_customuseragent.configure(state=tk.DISABLED)
        self.input_path.configure()
        self.path_download.set(get_init_dir())
        self.path_upload.set(get_init_dir())

    def __init__(self):
        super().__init__()

        self.make_window()

        # variables
        self.text_input_download = tk.StringVar()
        self.debug_open = tk.BooleanVar()
        self.verbose = tk.BooleanVar()
        self.proxy = tk.BooleanVar()
        self.path_download = tk.StringVar()
        self.path_upload = tk.StringVar()
        self.speedlimit = 0
        self.useragents = USERAGENTS
        self.errors = ERRORS

        # labels
        self.label_title = ttk.Label(
            self,
            text="cURL GUI",
            font=FONT_HEADER
        )
        self.label_download_url = ttk.Label(
            self,
            text="Hostname: ",
            font=FONT_TEXT
        )
        self.label_path_to_save = ttk.Label(
            self,
            text="Path to save file: ",
            font=FONT_TEXT
        )
        self.label_path_to_upload = ttk.Label(
            self,
            text="Path to upload file: ",
            font=FONT_TEXT
        )
        self.label_speedlimit = ttk.Label(
            self,
            text="Speed limit",
            font=FONT_SECTION
        )
        self.label_useragent = ttk.Label(
            self,
            text="User-agent",
            font=FONT_SECTION
        )
        self.label_httpbasicauth = ttk.Label(
            self,
            text="HTTP Basic authentication",
            font=FONT_SECTION
        )
        self.label_username = ttk.Label(self, text="Username", font=FONT_TEXT)
        self.label_password = ttk.Label(self, text="Password", font=FONT_TEXT)

        # entries
        self.input_download = ttk.Entry(
            self,
            width=50,
            textvariable=self.text_input_download
        )
        self.input_path = ttk.Entry(
            self,
            width=35,
            textvariable=self.path_download
        )
        self.input_upload = ttk.Entry(
            self,
            width=35,
            textvariable=self.path_upload
        )
        self.input_speedlimit = ttk.Entry(self, width=5)
        self.input_username = ttk.Entry(self, width=20)
        self.input_password = ttk.Entry(self, width=20)
        self.input_customuseragent = ttk.Entry(self, width=30)

        # buttons
        self.button_select_path = ttk.Button(
            self,
            text="Choose folder",
            command=self.ask_for_directory,
            width=13
        )
        self.button_download = ttk.Button(
            self,
            text="Download file",
            command=self.download_file,
            width=13
        )
        self.button_select_file = ttk.Button(
            self,
            text="Choose file",
            command=self.ask_for_file,
            width=13
        )
        self.button_upload = ttk.Button(
            self,
            text="Upload file",
            command=self.upload_file,
            width=13
        )
        self.button_debug = ttk.Button(
            self,
            text="Debug mode",
            command=self.debug_mode,
            width=13
        )
        self.button_proxy = ttk.Button(
            self,
            text="Set proxy",
            command=self.set_proxy,
            width=13,
            state=tk.DISABLED
        )
        self.button_cookies = ttk.Button(
            self,
            text="Set cookies",
            command=self.set_cookies,
            width=13
        )

        # combo boxes
        self.combobox_speedlimit = ttk.Combobox(
            self,
            values=['B/S', 'kB/S', 'MB/S', 'GB/S'],
            width=5,
            state="readonly"
        )
        self.combobox_useragent = ttk.Combobox(
            self,
            values=list(self.useragents),
            width=29,
            state="readonly"
        )

        # check buttons
        self.checkbutton_enable_proxy = ttk.Checkbutton(
            self,
            text="Enable proxy",
            variable=self.proxy,
            command=self.set_proxy_button,
        )

        # windows
        self.window_debug = DebugWindow(self)
        self.window_proxy = ProxyWindow(self)
        self.window_cookies = CookiesWindow(self)

        # other set functions
        self.set_positions()
        self.set_binds()
        self.set_currents()
