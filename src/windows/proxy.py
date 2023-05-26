import tkinter as tk

from tkinter import ttk


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
