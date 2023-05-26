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
    def show_info(message):
        messagebox.showinfo("Information", message)

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
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
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
            proxy_command += f"--proxy-user {username}:{password}"
            return proxy_command
        return True

    def get_useragent(self):
        selected_useragent = self.combobox_useragent.get()
        if selected_useragent == "Custom":
            useragent = self.input_customuseragent.get().strip()
            if not useragent:
                self.show_error("User-agent is empty")
                return False
        else:
            return self.useragents[selected_useragent]

        if useragent:
            return f"-A \"{useragent}\""
        else:
            self.show_error("Unknown user-agent")
            return False

    def get_httpbasicauth(self):
        username = self.input_username.get().strip()
        password = self.input_password.get().strip()

        return f"--user \"{username}:{password}\"" if username or password else ""

    def get_cookies(self):
        cookies = self.window_cookies.text_cookies.get("1.0", tk.END).split("\n")[:-1]
        cookies = ";".join(cookies)
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
        file_name = result.group(1) if result else self.text_input_download.get().replace("<>:\"/\\|?*", "")

        command = f"curl {cookies} {httpbasicauth} {useragent} {proxy_command} {verbose} --limit-rate {str(self.speedlimit)}{postfix} -o {path_to_save}/{file_name} -L {link_download}"
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

        command = f"curl {cookies} {httpbasicauth} {useragent} {proxy_command} {verbose} --limit-rate {str(self.speedlimit)}{postfix} -F file=@{file} -L {path_to_upload}"
        returncode = self.execute(command)
        message = self.errors[returncode]
        if message:
            self.show_error(message)
        else:
            self.show_info("File is downloaded successfully")

    def export_debug(self):
        self.create_logs_directory()
        today = datetime.datetime.today()
        formatted_date = today.strftime("%Y-%m-%d_%H-%M-%S")
        with open(f"logs/log_{formatted_date}.txt", "w") as f:
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
        self.label_title.place(x=175, y=10)
        self.label_download_url.place(x=10, y=100)
        self.label_path_to_save.place(x=10, y=130)
        self.label_path_to_upload.place(x=10, y=160)
        self.label_speedlimit.place(x=500, y=75)
        self.label_useragent.place(x=700, y=75)
        self.label_httpbasicauth.place(x=660, y=290)
        self.label_username.place(x=670, y=330)
        self.label_password.place(x=670, y=360)

        self.input_download.place(x=150, y=100)
        self.input_path.place(x=150, y=130)
        self.input_upload.place(x=150, y=160)
        self.input_speedlimit.place(x=500, y=100)
        self.input_username.place(x=750, y=330)
        self.input_password.place(x=750, y=360)
        self.input_customuseragent.place(x=700, y=130)

        self.button_select_path.place(x=460, y=125)
        self.button_download.place(x=550, y=125)
        self.button_select_file.place(x=460, y=155)
        self.button_upload.place(x=550, y=155)
        self.button_debug.place(x=350, y=250)
        self.button_proxy.place(x=450, y=250)
        self.button_cookies.place(x=400, y=300)

        self.combobox_speedlimit.place(x=550, y=100)
        self.combobox_useragent.place(x=700, y=100)

        self.checkbutton_enable_proxy.place(x=500, y=200)

    def set_binds(self):
        def on_entry_click_in(event):
            if self.text_input_download.get() == "http://":
                self.text_input_download.set("")

        def on_entry_click_out(event):
            if self.text_input_download.get() == "":
                self.text_input_download.set("http://")

        def on_custom(event):
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
        self.path.set(self.get_init_dir())

    def __init__(self):
        super().__init__()

        self.make_window()

        # variables
        self.text_input_download = tk.StringVar()
        self.debug_open = tk.BooleanVar()
        self.verbose = tk.BooleanVar()
        self.proxy = tk.BooleanVar()
        self.path = tk.StringVar()
        self.speedlimit = 0
        self.useragents = {
            'cURL': 'curl/7.68.0',
            'Mozilla Firefox / Linux (Ubuntu)': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0',
            'Mozilla Firefox / Windows 10': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0',
            'Mozilla Firefox / Windows 7': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0',
            'Mozilla Firefox / Mac OS X': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 12.5; rv:102.0) Gecko/20100101 Firefox/102.0',
            'Google Chrome / Linux': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
            'Google Chrome / Windows 10': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36',
            'Google Chrome / Windows 7': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
            'Google Chrome / Mac OS X': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
            'Safari / Mac OS X': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15',
            'Safari / IPhone': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Mobile/15E148 Safari/604.1',
            'Custom': ''
        }
        self.errors = {  # are taken from https://gist.github.com/gitkodak/b9c253e89397335356b13b37985778f5
            0: "",
            1: "Unsupported protocol. This build of curl has no support for this protocol.",
            2: "Failed to initialize.",
            3: "URL malformed. The syntax was not correct.",
            4: "A feature or option that was needed to perform the desired request was not enabled or was explicitly disabled at build-time. To make curl able to do this, you probably need another build of libcurl!",
            5: "Couldn't resolve proxy. The given proxy host could not be resolved.",
            6: "Couldn't resolve host. The given remote host was not resolved.",
            7: "Failed to connect to host.",
            8: "Weird server reply. The server sent data curl couldn't parse.",
            9: "FTP access denied. The server denied login or denied access to the particular resource or directory you wanted to reach. Most often you tried to change to a directory that doesn't exist on the server.",
            10: "FTP accept failed. While waiting for the server to connect back when an active FTP session is used, an error code was sent over the control connection or similar.",
            11: "FTP weird PASS reply. Curl couldn't parse the reply sent to the PASS request.",
            12: "During an active FTP session while waiting for the server to connect back to curl, the timeout expired.",
            13: "FTP weird PASV reply, Curl couldn't parse the reply sent to the PASV request.",
            14: "FTP weird 227 format. Curl couldn't parse the 227-line the server sent.",
            15: "FTP can't get host. Couldn't resolve the host IP we got in the 227-line.",
            16: "HTTP/2 error. A problem was detected in the HTTP2 framing layer. This is somewhat generic and can be one out of several problems, see the error message for details.",
            17: "FTP couldn't set binary. Couldn't change transfer method to binary.",
            18: "Partial file. Only a part of the file was transferred.",
            19: "FTP couldn't download/access the given file, the RETR (or similar) command failed.",
            21: "FTP quote error. A quote command returned error from the server.",
            22: "HTTP page not retrieved. The requested url was not found or returned another error with the HTTP error code being 400 or above. This return code only appears if -f, --fail is used.",
            23: "Write error. Curl couldn't write data to a local filesystem or similar.",
            25: "FTP couldn't STOR file. The server denied the STOR operation, used for FTP uploading.",
            26: "Read error. Various reading problems.",
            27: "Out of memory. A memory allocation request failed.",
            28: "Operation timeout. The specified time-out period was reached according to the conditions.",
            30: "FTP PORT failed. The PORT command failed. Not all FTP servers support the PORT command, try doing a transfer using PASV instead!",
            31: "FTP couldn't use REST. The REST command failed. This command is used for resumed FTP transfers.",
            33: "HTTP range error. The range \"command\" didn't work.",
            34: "HTTP post error. Internal post-request generation error.",
            35: "SSL connect error. The SSL handshaking failed.",
            36: "Bad download resume. Couldn't continue an earlier aborted download.",
            37: "FILE couldn't read file. Failed to open the file. Permissions?",
            38: "LDAP cannot bind. LDAP bind operation failed.",
            39: "LDAP search failed.",
            41: "Function not found. A required LDAP function was not found.",
            42: "Aborted by callback. An application told curl to abort the operation.",
            43: "Internal error. A function was called with a bad parameter.",
            45: "Interface error. A specified outgoing interface could not be used.",
            47: "Too many redirects. When following redirects, curl hit the maximum amount.",
            48: "Unknown option specified to libcurl. This indicates that you passed a weird option to curl that was passed on to libcurl and rejected. Read up in the manual!",
            49: "Malformed telnet option.",
            51: "The peer's SSL certificate or SSH MD5 fingerprint was not OK.",
            52: "The server didn't reply anything, which here is considered an error.",
            53: "SSL crypto engine not found.",
            54: "Cannot set SSL crypto engine as default.",
            55: "Failed sending network data.",
            56: "Failure in receiving network data.",
            58: "Problem with the local certificate.",
            59: "Couldn't use specified SSL cipher.",
            60: "Peer certificate cannot be authenticated with known CA certificates.",
            61: "Unrecognized transfer encoding.",
            62: "Invalid LDAP URL.",
            63: "Maximum file size exceeded.",
            64: "Requested FTP SSL level failed.",
            65: "Sending the data requires a rewind that failed.",
            66: "Failed to initialise SSL Engine.",
            67: "The user name, password, or similar was not accepted and curl failed to log in.",
            68: "File not found on TFTP server.",
            69: "Permission problem on TFTP server.",
            70: "Out of disk space on TFTP server.",
            71: "Illegal TFTP operation.",
            72: "Unknown TFTP transfer ID.",
            73: "File already exists (TFTP).",
            74: "No such user (TFTP).",
            75: "Character conversion failed.",
            76: "Character conversion functions required.",
            77: "Problem with reading the SSL CA cert (path? access rights?).",
            78: "The resource referenced in the URL does not exist.  ",
            79: "An unspecified error occurred during the SSH session.",
            80: "Failed to shut down the SSL connection.",
            82: "Could not load CRL file, missing or wrong format (added in 7.19.0).",
            83: "Issuer check failed (added in 7.19.0).",
            84: "The FTP PRET command failed",
            85: "RTSP: mismatch of CSeq numbers",
            86: "RTSP: mismatch of Session Identifiers",
            87: "unable to parse FTP file list",
            88: "FTP chunk callback reported error",
            89: "No connection available, the session will be queued",
            90: "SSL public key does not matched pinned public key",
            91: "Invalid SSL certificate status.",
            92: "Stream error in HTTP/2 framing layer."
        }

        # labels
        self.label_title = tk.Label(self, text="cURL GUI", font=("Arial", 20, "bold"))
        self.label_download_url = tk.Label(self, text="Download URL: ", font=("Arial", 11))
        self.label_path_to_save = tk.Label(self, text="Path to save file: ", font=("Arial", 11))
        self.label_path_to_upload = tk.Label(self, text="Path to upload file: ", font=("Arial", 11))
        self.label_speedlimit = tk.Label(self, text="Speed limit", font=("Arial", 11))
        self.label_useragent = tk.Label(self, text="Choose user-agent", font=("Arial", 11))
        self.label_httpbasicauth = tk.Label(self, text="HTTP Basic authentication", font=("Arial", 14))
        self.label_username = tk.Label(self, text="Username", font=("Arial", 11))
        self.label_password = tk.Label(self, text="Password", font=("Arial", 11))

        # entries
        self.input_download = tk.Entry(self, width=50, textvariable=self.text_input_download)
        self.input_path = tk.Entry(self, width=50, textvariable=self.path)
        self.input_upload = tk.Entry(self, width=50, textvariable=self.path)
        self.input_speedlimit = tk.Entry(self, width=5)
        self.input_username = tk.Entry(self, width=20)
        self.input_password = tk.Entry(self, width=20)
        self.input_customuseragent = tk.Entry(self, width=50)

        # buttons
        self.button_select_path = tk.Button(self, text="Choose folder", command=self.ask_for_directory)
        self.button_download = tk.Button(self, text="Download file", command=self.download_file)
        self.button_select_file = tk.Button(self, text="Choose file", command=self.ask_for_file)
        self.button_upload = tk.Button(self, text="Upload file", command=self.upload_file)
        self.button_debug = tk.Button(self, text="Debug mode", command=self.debug_mode)
        self.button_proxy = tk.Button(self, text="Set proxy", command=self.set_proxy, state=tk.DISABLED)
        self.button_cookies = tk.Button(self, text="Set cookies", command=self.set_cookies)

        # combo boxes
        self.combobox_speedlimit = ttk.Combobox(self, values=['B/S', 'kB/S', 'MB/S', 'GB/S'], width=5, state="readonly")
        self.combobox_useragent = ttk.Combobox(self, values=list(self.useragents), width=30, state="readonly")

        # check buttons
        self.checkbutton_enable_proxy = ttk.Checkbutton(self, text="Enable proxy", variable=self.proxy,
                                                        command=self.set_proxy_button)

        # windows
        self.window_debug = DebugWindow(self)
        self.window_proxy = ProxyWindow(self)
        self.window_cookies = CookiesWindow(self)

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

        self.text_logs = tk.Text(self, state=tk.DISABLED, width=100, height=25)

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

        self.protocols = [
            'HTTP',
            'HTTPS',
            'SOCKS4',
            'SOCKS5',
        ]

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

        self.combobox_protocol = ttk.Combobox(self, values=self.protocols, width=10, state="readonly")

        self.set_positions()
        self.set_currents()


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

        self.label_information = tk.Label(self, text="Write your cookies in format cookie1=value1 \n Divide cookies by new line", font=("Arial", 14))

        self.text_cookies = tk.Text(self, width=48, height=14)

        self.set_positions()


# todo переместить это все нахуй по классам и отдельным файлам
if __name__ == "__main__":
    app = Application()
    app.mainloop()
