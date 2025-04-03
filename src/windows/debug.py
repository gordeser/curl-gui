import tkinter as tk

from tkinter import ttk


class DebugWindow(tk.Toplevel):

    def make_window(self):
        self.title("Debug mode")
        self.geometry("805x500")
        self.resizable(False, False)
        self.withdraw()

    def set_positions(self):
        self.checkbutton_verbose.place(x=10, y=460)
        self.button_export_debug.place(x=690, y=460)
        self.button_clear_logs.place(x=375, y=460)
        self.text_logs.place(x=0, y=0)

    def clear_logs(self):
        self.text_logs.config(state=tk.NORMAL)
        self.text_logs.delete("1.0", tk.END)
        self.text_logs.config(state=tk.DISABLED)

    def __init__(self, parent):
        super().__init__(parent)
        self.make_window()

        self.checkbutton_verbose = ttk.Checkbutton(
            self,
            text="Verbose mode",
            variable=parent.verbose,
            width=13
        )

        self.button_export_debug = ttk.Button(
            self,
            text="Export logs to file",
            command=parent.export_debug
        )
        self.button_clear_logs = ttk.Button(
            self,
            text="Clear logs",
            command=self.clear_logs,
            width=13
        )

        self.text_logs = tk.Text(self, state=tk.DISABLED, width=100, height=25)

        self.set_positions()
