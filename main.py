import tkinter as tk


class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("cURL GUI")
        self.geometry("500x500")

        self.label = tk.Label(self, text="cURL GUI", font=("Helvetica", 20, "bold"))
        # self.label.grid(padx=10, pady=10, sticky="n")
        self.label.pack(pady=20)


if __name__ == "__main__":
    app = Application()
    app.mainloop()


