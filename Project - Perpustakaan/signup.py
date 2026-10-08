import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

from config import (
    COLOR_BG, COLOR_CARD, COLOR_TEXT, COLOR_MUTED, COLOR_ACCENT,
    COLOR_ACCENT_DARK, FONT_LABEL, FONT_BUTTON, HoverButton, register_user
)


class SignUpPage(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BG)

        self.controller = controller

        self.password_visible = False
        self.confirm_visible = False

        # CONTAINER UTAMA

        container = tk.Frame(self, bg=COLOR_BG)
        container.pack(fill="both", expand=True)

        # PANEL KIRI

        left_panel = tk.Frame(container, width=420, bg="white")

        left_panel.pack(side="left", fill="y")
        left_panel.pack_propagate(False)

        try:
            image = Image.open("daftar.png")

            image = image.resize((420, 720), Image.Resampling.LANCZOS)

            self.left_image = ImageTk.PhotoImage(image)

            tk.Label(left_panel, image=self.left_image, borderwidth=0).pack(fill="both", expand=True)

        except Exception:
            tk.Label(left_panel, text="SIGN UP IMAGE", font=("Segoe UI", 24, "bold")).pack(expand=True)

        # PANEL KANAN

        right_panel = tk.Frame(container, bg=COLOR_BG)

        right_panel.pack(side="left", fill="both", expand=True)

        card = tk.Frame(right_panel, bg=COLOR_CARD, highlightthickness=2, highlightbackground="#90b8d0")

        card.pack(fill="both", expand=True, padx=40, pady=40)

        content = tk.Frame(card, bg=COLOR_CARD)

        content.pack(fill="both", expand=True, padx=35, pady=25)

        # JUDUL

        tk.Label(content, text="Daftar Akun", bg=COLOR_CARD, fg=COLOR_TEXT, font=("Segoe UI", 24, "bold")).pack(anchor="w", pady=(0, 20))

        # NAMA

        tk.Label(content, text="Nama Lengkap", bg=COLOR_CARD, fg=COLOR_TEXT, font=("Segoe UI", 11, "bold")).pack(anchor="w")

        self.entry_nama = tk.Entry(content, font=FONT_LABEL, relief="solid", bd=1)

        self.entry_nama.pack(fill="x", ipady=8, pady=(4, 12))

        # USERNAME

        tk.Label(content, text="Username", bg=COLOR_CARD, fg=COLOR_TEXT, font=("Segoe UI", 11, "bold")).pack(anchor="w")

        self.entry_username = tk.Entry(content, font=FONT_LABEL, relief="solid", bd=1)

        self.entry_username.pack(fill="x", ipady=8, pady=(4, 12))

        # EMAIL

        tk.Label(content, text="Email", bg=COLOR_CARD, fg=COLOR_TEXT, font=("Segoe UI", 11, "bold")).pack(anchor="w")

        self.entry_email = tk.Entry(content, font=FONT_LABEL, relief="solid", bd=1)

        self.entry_email.pack(fill="x", ipady=8, pady=(4, 12))

        # PASSWORD

        tk.Label(content, text="Password", bg=COLOR_CARD, fg=COLOR_TEXT, font=("Segoe UI", 11, "bold")).pack(anchor="w")

        password_frame = tk.Frame(content, bg=COLOR_CARD)

        password_frame.pack(fill="x", pady=(4, 12))

        self.entry_password = tk.Entry(password_frame, font=FONT_LABEL, show="*", relief="solid", bd=1)

        self.entry_password.pack(side="left", fill="x", expand=True, ipady=8)

        self.btn_password = tk.Button(password_frame, text="👁", width=4, command=self.toggle_password)

        self.btn_password.pack(side="right", padx=(5, 0))

        # KONFIRMASI PASSWORD

        tk.Label(content, text="Konfirmasi Password", bg=COLOR_CARD, fg=COLOR_TEXT, font=("Segoe UI", 11, "bold")).pack(anchor="w")

        confirm_frame = tk.Frame(content, bg=COLOR_CARD)

        confirm_frame.pack(fill="x", pady=(4, 20))

        self.entry_confirm = tk.Entry(confirm_frame, font=FONT_LABEL, show="*", relief="solid", bd=1)

        self.entry_confirm.pack(side="left", fill="x", expand=True, ipady=8)

        self.btn_confirm = tk.Button(confirm_frame, text="👁", width=4, command=self.toggle_confirm_password)

        self.btn_confirm.pack(side="right", padx=(5, 0))

        self.entry_confirm.bind("<Return>", lambda e: self.handle_signup())

        # TOMBOL DAFTAR

        HoverButton(
            content, bg_normal=COLOR_ACCENT, bg_hover=COLOR_ACCENT_DARK, text="Daftar",
            fg="white", bd=0, cursor="hand2", font=FONT_BUTTON, command=self.handle_signup
        ).pack(fill="x", ipady=12)

        # LOGIN

        bottom_frame = tk.Frame(content, bg=COLOR_CARD)

        bottom_frame.pack(pady=(20, 0))

        tk.Label(bottom_frame, text="Sudah punya akun ?", bg=COLOR_CARD, fg=COLOR_TEXT, font=FONT_LABEL).pack(side="left")

        login_link = tk.Label(
            bottom_frame, text=" Login", bg=COLOR_CARD, fg=COLOR_ACCENT,
            cursor="hand2", font=("Segoe UI", 11, "bold", "underline")
        )

        login_link.pack(side="left")

        login_link.bind("<Button-1>", lambda e: controller.show_frame("SignInPage"))

        back = tk.Label(content, text="← Kembali ke Beranda", bg=COLOR_CARD, fg=COLOR_MUTED, cursor="hand2", font=("Segoe UI", 10, "underline"))

        back.pack(pady=(20, 0))

        back.bind("<Button-1>", lambda e: controller.show_frame("HomePage"))

    # SHOW/HIDE PASSWORD

    def toggle_password(self):

        self.password_visible = not self.password_visible

        if self.password_visible:
            self.entry_password.config(show="")
            self.btn_password.config(text="🙈")
        else:
            self.entry_password.config(show="*")
            self.btn_password.config(text="👁")

    # SHOW/HIDE KONFIRMASI PASSWORD

    def toggle_confirm_password(self):

        self.confirm_visible = not self.confirm_visible

        if self.confirm_visible:
            self.entry_confirm.config(show="")
            self.btn_confirm.config(text="🙈")
        else:
            self.entry_confirm.config(show="*")
            self.btn_confirm.config(text="👁")

    # DAFTAR

    def handle_signup(self):

        nama = self.entry_nama.get().strip()
        username = self.entry_username.get().strip()
        email = self.entry_email.get().strip()
        password = self.entry_password.get()
        confirm = self.entry_confirm.get()

        if not nama:
            messagebox.showwarning("Data Belum Lengkap", "Masukkan nama lengkap.")
            return

        if not username:
            messagebox.showwarning("Data Belum Lengkap", "Masukkan username.")
            return

        if not email:
            messagebox.showwarning("Data Belum Lengkap", "Masukkan email.")
            return

        if "@" not in email or "." not in email:
            messagebox.showwarning("Email Tidak Valid", "Masukkan format email yang benar.")
            return

        if len(password) < 8:
            messagebox.showwarning("Password Tidak Valid", "Password minimal 8 karakter.")
            return

        if password != confirm:
            messagebox.showwarning("Password Tidak Cocok", "Konfirmasi password harus sama.")
            return

        success, message = register_user(nama, username, email, password)

        if success:

            messagebox.showinfo("Berhasil", message)

            self.clear_fields()

            self.controller.show_frame("SignInPage")

        else:

            messagebox.showerror("Gagal Mendaftar", message)

    # CLEAR FORM

    def clear_fields(self):

        self.entry_nama.delete(0, tk.END)
        self.entry_username.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)
        self.entry_password.delete(0, tk.END)
        self.entry_confirm.delete(0, tk.END)

    def on_show(self):
        self.clear_fields()