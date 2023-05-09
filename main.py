import tkinter as tk


class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("cURL GUI")
        self.geometry("500x500")

        self.label_title = tk.Label(self, text="cURL GUI", font=("Arial", 20, "bold"))
        self.label_title.place(x=175, y=10)

        self.label_download = tk.Label(self, text="Download URL: ", font=("Arial", 11))
        self.label_download.place(x=10, y=100)




if __name__ == "__main__":
    app = Application()
    app.mainloop()


