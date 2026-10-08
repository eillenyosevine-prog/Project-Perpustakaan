import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

from config import (
    COLOR_BG, COLOR_CARD, COLOR_TEXT, COLOR_MUTED, COLOR_ACCENT,
    COLOR_ACCENT_DARK, FONT_LABEL, FONT_BUTTON, HoverButton, verify_login
)


class SignInPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BG)

        self.controller = controller
        self.password_visible = False

        # CONTAINER UTAMA

        container = tk.Frame(self, bg=COLOR_BG)
        container.pack(fill="both", expand=True)

        # PANEL KIRI

        left_panel = tk.Frame(container, width=420, bg="white")

        left_panel.pack(side="left", fill="y")
        left_panel.pack_propagate(False)

        image = Image.open("login.png")

        image = image.resize((420, 720))

        self.left_image = ImageTk.PhotoImage(image)

        image_label = tk.Label(left_panel, image=self.left_image, borderwidth=0)

        image_label.pack(fill="both", expand=True)

        # PANEL KANAN (2/3)

        right_panel = tk.Frame(container, bg=COLOR_BG)
        right_panel.pack(side="left", fill="both", expand=True)

        card = tk.Frame(right_panel, bg=COLOR_CARD, highlightthickness=2, highlightbackground="#90b8d0")

        card.pack(fill="both", expand=True, padx=40, pady=40)

        content = tk.Frame(card, bg=COLOR_CARD)

        content.pack(fill="both", expand=True, padx=35, pady=30)

        # JUDUL

        tk.Label(content, text="Selamat Datang!", bg=COLOR_CARD, fg=COLOR_TEXT, font=("Segoe UI", 24, "bold")).pack(anchor="w")

        tk.Label(content, text="Masuk ke akun Anda untuk melanjutkan", bg=COLOR_CARD, fg=COLOR_MUTED, font=("Segoe UI", 12)).pack(anchor="w", pady=(0, 30))

        # USERNAME

        tk.Label(content, text="Username", bg=COLOR_CARD, fg=COLOR_TEXT, font=("Segoe UI", 12, "bold")).pack(anchor="w")

        self.entry_username = tk.Entry(content, font=FONT_LABEL, relief="solid", bd=1)

        self.entry_username.pack(fill="x", ipady=10, pady=(5, 20))

        # PASSWORD

        tk.Label(content, text="Password", bg=COLOR_CARD, fg=COLOR_TEXT, font=("Segoe UI", 12, "bold")).pack(anchor="w")

        password_frame = tk.Frame(content, bg=COLOR_CARD)

        password_frame.pack(fill="x", pady=(5, 10))

        self.entry_password = tk.Entry(password_frame, font=FONT_LABEL, show="*", relief="solid", bd=1)

        self.entry_password.pack(side="left", fill="x", expand=True, ipady=10)

        self.btn_toggle = tk.Button(password_frame, text="👁", width=4, command=self.toggle_password)

        self.btn_toggle.pack(side="right", padx=(5, 0))

        self.entry_password.bind("<Return>", lambda e: self.handle_signin())

        # OPSI

        option_frame = tk.Frame(content, bg=COLOR_CARD)

        option_frame.pack(fill="x", pady=(5, 25))

        self.remember_var = tk.BooleanVar()

        tk.Checkbutton(option_frame, text="Ingatkan Saya", variable=self.remember_var, bg=COLOR_CARD).pack(side="left")

        forgot = tk.Label(option_frame, text="Lupa Password?", bg=COLOR_CARD, fg="#3f51b5", cursor="hand2", font=("Segoe UI", 10, "underline"))

        forgot.pack(side="right")

        forgot.bind("<Button-1>", lambda e: messagebox.showinfo("Lupa Password", "Silakan hubungi administrator."))

        # LOGIN

        HoverButton(
            content, bg_normal=COLOR_ACCENT, bg_hover=COLOR_ACCENT_DARK, text="Login",
            fg="white", bd=0, font=FONT_BUTTON, cursor="hand2", command=self.handle_signin
        ).pack(fill="x", ipady=12)

        tk.Label(content, text="atau", bg=COLOR_CARD, fg=COLOR_MUTED, font=("Segoe UI", 11)).pack(pady=15)

        # DAFTAR

        tk.Button(
            content, text="Daftar Akun Baru", font=("Segoe UI", 12, "bold"), bg="white",
            relief="solid", bd=1, cursor="hand2", command=lambda: controller.show_frame("SignUpPage")
        ).pack(fill="x", ipady=12)

        # KEMBALI

        back = tk.Label(content, text="← Kembali ke Beranda", bg=COLOR_CARD, fg=COLOR_MUTED, cursor="hand2", font=("Segoe UI", 10, "underline"))

        back.pack(pady=(25, 0))

        back.bind("<Button-1>", lambda e: controller.show_frame("HomePage"))

    # SHOW/HIDE PASSWORD

    def toggle_password(self):
        self.password_visible = not self.password_visible

        if self.password_visible:
            self.entry_password.config(show="")
            self.btn_toggle.config(text="🙈")
        else:
            self.entry_password.config(show="*")
            self.btn_toggle.config(text="👁")

    # LOGIN

    def handle_signin(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get()

        if not username or not password:
            messagebox.showwarning("Data Belum Lengkap", "Mohon isi username dan password.")
            return

        if len(password) < 8:
            messagebox.showwarning("Password Tidak Valid", "Password minimal 8 karakter.")
            return

        success, message = verify_login(username, password)

        if success:
            self.controller.set_current_user(username)

            messagebox.showinfo("Berhasil", f"{message}\nSelamat datang, {username}!")

            self.clear_fields()

            self.controller.show_frame("HomePage")

        else:
            messagebox.showerror("Login Gagal", message)

    def clear_fields(self):
        self.entry_username.delete(0, tk.END)
        self.entry_password.delete(0, tk.END)

    def on_show(self):
        self.clear_fields()