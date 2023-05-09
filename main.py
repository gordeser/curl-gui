import tkinter as tk


class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("cURL GUI")
        self.geometry('500x500')


if __name__ == "__main__":
    app = Application()
    app.mainloop()


