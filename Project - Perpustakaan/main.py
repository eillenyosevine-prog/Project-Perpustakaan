import tkinter as tk

from config import APP_WIDTH, APP_HEIGHT, COLOR_BG
from homepage import HomePage
from signup import SignUpPage
from signin import SignInPage
from bookmanagement import BookManagementPage
from borrowingmanagement import BorrowingManagementPage
from usersmanagement import UsersManagementPage


class PerpustakaanApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PerpustakaanKu")
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.resizable(False, False)
        self.configure(bg=COLOR_BG)

        self.current_user = None

        container = tk.Frame(self, bg=COLOR_BG)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for PageClass in (HomePage, SignUpPage, SignInPage, BookManagementPage, BorrowingManagementPage, UsersManagementPage):
            page_name = PageClass.__name__
            frame = PageClass(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("HomePage")

    def show_frame(self, page_name: str):
        frame = self.frames[page_name]
        if hasattr(frame, "on_show"):
            frame.on_show()
        frame.tkraise()

    def set_current_user(self, username: str):
        self.current_user = username

    def logout(self):
        self.current_user = None
        self.show_frame("HomePage")


if __name__ == "__main__":
    app = PerpustakaanApp()
    app.mainloop()