import tkinter as tk
from tkinter import ttk, messagebox
import re

from config import (
    COLOR_PRIMARY, COLOR_ACCENT, COLOR_ACCENT_DARK, COLOR_TEXT, 
    COLOR_MUTED, COLOR_SUCCESS, COLOR_DANGER, HoverButton, 
    load_users, register_user, update_user, delete_user, save_users
)


class UsersManagementPage(tk.Frame):
    BG = "#f7f8fa"
    WHITE = "#ffffff"
    BORDER = "#d9dde3"
    ACTIVE_BLUE = "#b9dcf5"
    HEADER_BG = "#f1f3f5"
    YELLOW = "#f4d03f"
    BLUE = "#2980b9"
    DARK_BLUE = "#1c5980"
    RED = "#c0392b"
    GREEN = "#27ae60"

    ROW_HEIGHT = 58
    PER_PAGE = 5

    def __init__(self, parent, controller):
        super().__init__(parent, bg=self.BG)
        self.controller = controller

        self.search_var = tk.StringVar()
        self.role_var = tk.StringVar(value="Semua Peran")
        self.current_page = 1
        self.filtered_users = []

        self.build_sidebar()
        self.build_content()
        self.refresh_table()

    # SIDEBAR

    def build_sidebar(self):
        self.sidebar = tk.Frame(self, bg=self.WHITE, width=260, highlightbackground="#d0d0d0", highlightthickness=1)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        logo_frame = tk.Frame(self.sidebar, bg=COLOR_PRIMARY, height=100)
        logo_frame.pack(fill="x")
        logo_frame.pack_propagate(False)

        tk.Label(logo_frame, text="📚 PerpustakaanKu", bg=COLOR_PRIMARY, fg="white", font=("Segoe UI", 17, "bold")).pack(expand=True)

        menu_frame = tk.Frame(self.sidebar, bg=self.WHITE)
        menu_frame.pack(fill="both", expand=True)

        self.create_menu_button(menu_frame, "🏠  Beranda", False, lambda: self.controller.show_frame("HomePage"))
        self.create_menu_button(menu_frame, "👥  Kelola User", True, lambda: self.controller.show_frame("UsersManagementPage"))
        self.create_menu_button(menu_frame, "📖  Kelola Buku", False, lambda: self.controller.show_frame("BookManagementPage"))
        self.create_menu_button(menu_frame, "🔄  Kelola Peminjaman", False, lambda: self.controller.show_frame("BorrowingManagementPage"))

        tk.Frame(menu_frame, bg=self.WHITE).pack(fill="both", expand=True)
        self.create_menu_button(menu_frame, "➜]  Logout", False, self.controller.logout, danger=True)

    def create_menu_button(self, parent, text, active, command, danger=False):
        bg_normal = self.ACTIVE_BLUE if active else self.WHITE
        bg_hover = self.ACTIVE_BLUE if active else "#eef2f5"
        fg = self.RED if danger else COLOR_TEXT

        button = HoverButton(parent, text=text, bg_normal=bg_normal, bg_hover=bg_hover, fg=fg,
                             font=("Segoe UI", 12, "bold" if active else "normal"), relief="flat", bd=0,
                             anchor="w", padx=22, cursor="hand2", command=command)
        button.pack(fill="x", ipady=13)
        return button

    # KONTEN UTAMA

    def build_content(self):
        self.content = tk.Frame(self, bg=self.BG)
        self.content.pack(side="left", fill="both", expand=True)

        # Header bar
        header = tk.Frame(self.content, bg=self.BG, height=80)
        header.pack(fill="x", padx=30, pady=(10, 0))
        header.pack_propagate(False)

        tk.Label(header, text="Kelola User", bg=self.BG, fg="#222222", font=("Segoe UI", 22, "bold")).pack(side="left", pady=20)

        user_frame = tk.Frame(header, bg=self.BG)
        user_frame.pack(side="right", pady=15)
        tk.Label(user_frame, text="👤", bg=self.BG, fg="#2c3e50", font=("Segoe UI", 16)).pack(side="left", padx=(0, 6))

        self.user_label = tk.Label(user_frame, text="Admin", bg=self.BG, fg=COLOR_TEXT, font=("Segoe UI", 12, "bold"))
        self.user_label.pack(side="left")

        tk.Frame(self.content, bg="#bfc3c7", height=1).pack(fill="x", padx=30)

        # Top Bar (Filter, Search)
        top_bar = tk.Frame(self.content, bg=self.BG)
        top_bar.pack(fill="x", padx=30, pady=(25, 18))

        search_frame = tk.Frame(top_bar, bg=self.WHITE, highlightbackground="#bfc3c7", highlightthickness=1)
        search_frame.pack(side="left", fill="x", expand=True, padx=(0, 12))

        tk.Label(search_frame, text="🔍︎", bg=self.WHITE, fg="#777777", font=("Segoe UI", 11)).pack(side="left", padx=(10, 5))

        self.entry_search = tk.Entry(search_frame, textvariable=self.search_var, bg=self.WHITE, fg="#555555", relief="flat", bd=0, font=("Segoe UI", 11))
        self.entry_search.pack(side="left", fill="x", expand=True, ipady=9)
        self.entry_search.insert(0, "Cari nama, username, atau email")
        self.entry_search.config(fg="#999999")
        self.entry_search.bind("<FocusIn>", self.clear_placeholder)
        self.entry_search.bind("<FocusOut>", self.restore_placeholder)
        self.entry_search.bind("<KeyRelease>", self.on_search)

        self.role_combo = ttk.Combobox(top_bar, textvariable=self.role_var, values=["Semua Peran", "Admin", "Pustakawan", "Anggota"], state="readonly", font=("Segoe UI", 10), width=18)
        self.role_combo.pack(side="left", padx=(0, 12), ipady=7)
        self.role_combo.bind("<<ComboboxSelected>>", self.on_filter)

        tk.Button(top_bar, text="+ Tambah User", bg=self.BLUE, fg="white", activebackground=self.DARK_BLUE, activeforeground="white",
                  font=("Segoe UI", 11, "bold"), relief="flat", bd=0, cursor="hand2", command=self.open_add_user).pack(side="right", ipadx=16, ipady=9)

        # Table Container Card
        self.table_card = tk.Frame(self.content, bg=self.WHITE, highlightbackground="#c9cdd1", highlightthickness=1)
        self.table_card.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        # Table Header
        self.table_header = tk.Frame(self.table_card, bg=self.HEADER_BG, height=50)
        self.table_header.pack(fill="x")
        self.table_header.pack_propagate(False)

        columns = [("No", 55), ("Nama", 160), ("Username", 130), ("Email", 210), ("Peran", 110), ("Status", 100), ("Aksi", 130)]
        for title, width in columns:
            frame = tk.Frame(self.table_header, bg=self.HEADER_BG, width=width)
            frame.pack(side="left", fill="y")
            frame.pack_propagate(False)
            tk.Label(frame, text=title, bg=self.HEADER_BG, fg=COLOR_TEXT, font=("Segoe UI", 10, "bold"), anchor="center").pack(fill="both", expand=True)

        # Table Rows Container
        self.canvas_container = tk.Frame(self.table_card, bg=self.WHITE)
        self.canvas_container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.canvas_container, bg=self.WHITE, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.canvas_container, orient="vertical", command=self.canvas.yview)
        self.rows_frame = tk.Frame(self.canvas, bg=self.WHITE)

        self.canvas_window = self.canvas.create_window((0, 0), window=self.rows_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.rows_frame.bind("<Configure>", self.update_scroll_region)
        self.canvas.bind("<Configure>", self.resize_canvas_window)

        # Footer / Pagination
        footer = tk.Frame(self.table_card, bg=self.WHITE, height=60)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        self.data_label = tk.Label(footer, text="Menampilkan 0-0 dari 0 data", bg=self.WHITE, fg=COLOR_TEXT, font=("Segoe UI", 10))
        self.data_label.pack(side="left", padx=20)

        pagination = tk.Frame(footer, bg=self.WHITE)
        pagination.pack(side="right", padx=15)

        self.prev_button = tk.Button(pagination, text="‹", bg="#eeeeee", fg=COLOR_TEXT, activebackground="#dddddd", relief="flat", bd=0, font=("Segoe UI", 13, "bold"), width=4, command=self.previous_page)
        self.prev_button.pack(side="left", padx=3)

        self.page_label = tk.Label(pagination, text="1", bg=self.BLUE, fg="white", font=("Segoe UI", 10, "bold"), width=4)
        self.page_label.pack(side="left", padx=3, ipady=6)

        self.next_button = tk.Button(pagination, text="›", bg="#eeeeee", fg=COLOR_TEXT, activebackground="#dddddd", relief="flat", bd=0, font=("Segoe UI", 13, "bold"), width=4, command=self.next_page)
        self.next_button.pack(side="left", padx=3)

    # PLACEHOLDER & SEARCH HANDLER

    def clear_placeholder(self, event=None):
        if self.search_var.get() == "Cari nama, username, atau email":
            self.search_var.set("")
            self.entry_search.config(fg="#555555")

    def restore_placeholder(self, event=None):
        if not self.search_var.get().strip():
            self.search_var.set("Cari nama, username, atau email")
            self.entry_search.config(fg="#999999")

    def on_search(self, event=None):
        self.current_page = 1
        self.refresh_table()

    def on_filter(self, event=None):
        self.current_page = 1
        self.refresh_table()

    # REFRESH TABEL

    def refresh_table(self):
        for widget in self.rows_frame.winfo_children():
            widget.destroy()

        try:
            users = load_users()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membaca data user:\n\n{e}")
            return

        search_text = self.search_var.get().strip().lower()
        if search_text == "cari nama, username, atau email":
            search_text = ""

        selected_role = self.role_var.get()
        self.filtered_users = []

        for username, data in users.items():
            if not isinstance(data, dict):
                continue

            nama = str(data.get("nama", "-"))
            email = str(data.get("email", "-"))
            role = str(data.get("role", "Anggota"))
            status = str(data.get("status", "Aktif"))

            target = f"{nama} {username} {email} {role} {status}".lower()

            if search_text and search_text not in target:
                continue
            if selected_role != "Semua Peran" and role != selected_role:
                continue

            self.filtered_users.append((username, data))

        total_data = len(self.filtered_users)
        total_pages = max(1, (total_data + self.PER_PAGE - 1) // self.PER_PAGE)

        if self.current_page > total_pages:
            self.current_page = total_pages

        start_index = (self.current_page - 1) * self.PER_PAGE
        end_index = min(start_index + self.PER_PAGE, total_data)
        page_data = self.filtered_users[start_index:end_index]

        if not page_data:
            empty_frame = tk.Frame(self.rows_frame, bg=self.WHITE, height=100)
            empty_frame.pack(fill="x")
            empty_frame.pack_propagate(False)
            tk.Label(empty_frame, text="Tidak ada data user.", bg=self.WHITE, fg=COLOR_MUTED, font=("Segoe UI", 11)).pack(expand=True)
        else:
            for index, (username, data) in enumerate(page_data):
                actual_number = start_index + index + 1
                self.create_user_row(actual_number, username, data)

        if total_data == 0:
            self.data_label.config(text="Menampilkan 0-0 dari 0 data")
        else:
            self.data_label.config(text=f"Menampilkan {start_index + 1}-{end_index} dari {total_data} data")

        self.page_label.config(text=str(self.current_page))
        self.prev_button.config(state="normal" if self.current_page > 1 else "disabled")
        self.next_button.config(state="normal" if self.current_page < total_pages else "disabled")

        self.canvas.yview_moveto(0)
        self.rows_frame.update_idletasks()

    # CREATING ROW

    def create_user_row(self, number, username, data):
        nama = data.get("nama", "-")
        email = data.get("email", "-")
        role = data.get("role", "Anggota")
        status = data.get("status", "Aktif")

        row = tk.Frame(self.rows_frame, bg=self.WHITE, height=self.ROW_HEIGHT)
        row.pack(fill="x")
        row.pack_propagate(False)

        widths = [55, 160, 130, 210, 110, 100, 130]

        # No
        self.create_cell(row, str(number), widths[0], anchor="center")

        # Nama
        nama_frame = tk.Frame(row, bg=self.WHITE, width=widths[1])
        nama_frame.pack(side="left", fill="y")
        nama_frame.pack_propagate(False)
        tk.Label(nama_frame, text="👤 ", bg=self.WHITE, fg="#555555", font=("Segoe UI", 10)).pack(side="left", padx=(8, 0))
        tk.Label(nama_frame, text=nama, bg=self.WHITE, fg=COLOR_TEXT, font=("Segoe UI", 10), anchor="w").pack(side="left", fill="both", expand=True)

        # Username & Email
        self.create_cell(row, username, widths[2], anchor="w")
        self.create_cell(row, email, widths[3], anchor="w")

        # Role
        role_frame = tk.Frame(row, bg=self.WHITE, width=widths[4])
        role_frame.pack(side="left", fill="y")
        role_frame.pack_propagate(False)
        role_color = {"Admin": "#8e44ad", "Pustakawan": "#2980b9", "Anggota": "#16a085"}.get(role, "#7f8c8d")
        tk.Label(role_frame, text=role, bg=role_color, fg="white", font=("Segoe UI", 8, "bold"), padx=8).pack(padx=8, pady=17)

        # Status
        status_frame = tk.Frame(row, bg=self.WHITE, width=widths[5])
        status_frame.pack(side="left", fill="y")
        status_frame.pack_propagate(False)
        status_color = self.GREEN if status == "Aktif" else self.RED
        tk.Label(status_frame, text=status, bg=status_color, fg="white", font=("Segoe UI", 8, "bold"), padx=8).pack(padx=8, pady=17)

        # Aksi
        action_frame = tk.Frame(row, bg=self.WHITE, width=widths[6])
        action_frame.pack(side="left", fill="y")
        action_frame.pack_propagate(False)

        action_container = tk.Frame(action_frame, bg=self.WHITE)
        action_container.pack(expand=True)

        tk.Button(action_container, text="✏️", bg=self.YELLOW, fg="#333333", activebackground="#e5c331", relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 10), width=3, height=1, command=lambda u=username: self.open_edit_user(u)).pack(side="left", padx=3)
        tk.Button(action_container, text="    🗑️", bg="#f5b7b1", fg=self.RED, activebackground="#ec7063", relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 10), width=3, height=1, command=lambda u=username: self.delete_user_action(u)).pack(side="left", padx=3)

        tk.Frame(self.rows_frame, bg=self.BORDER, height=1).pack(fill="x")

    def create_cell(self, parent, text, width, anchor="w"):
        frame = tk.Frame(parent, bg=self.WHITE, width=width)
        frame.pack(side="left", fill="y")
        frame.pack_propagate(False)
        tk.Label(frame, text=text, bg=self.WHITE, fg=COLOR_TEXT, font=("Segoe UI", 10), anchor=anchor).pack(fill="both", expand=True, padx=8)

    # PAGINATION & SCROLLING

    def previous_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.refresh_table()

    def next_page(self):
        total_data = len(self.filtered_users)
        total_pages = max(1, (total_data + self.PER_PAGE - 1) // self.PER_PAGE)
        if self.current_page < total_pages:
            self.current_page += 1
            self.refresh_table()

    def update_scroll_region(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def resize_canvas_window(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    # TAMBAH & EDIT USER

    def open_add_user(self):
        window = tk.Toplevel(self)
        window.title("Tambah User")
        window.geometry("460x640")
        window.resizable(False, False)
        window.configure(bg=self.WHITE)
        self.center_window(window, 460, 640)

        tk.Label(window, text="Tambah User", bg=self.WHITE, fg=COLOR_TEXT, font=("Segoe UI", 19, "bold")).pack(pady=(25, 20))
        form = tk.Frame(window, bg=self.WHITE)
        form.pack(fill="x", padx=40)

        nama_entry = self.create_form_entry(form, "Nama Lengkap")
        username_entry = self.create_form_entry(form, "Username")
        email_entry = self.create_form_entry(form, "Email")
        password_entry = self.create_form_entry(form, "Password", show="*")

        tk.Label(form, text="Peran", bg=self.WHITE, fg=COLOR_TEXT, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        role_combo = ttk.Combobox(form, values=["Admin", "Pustakawan", "Anggota"], state="readonly", font=("Segoe UI", 10))
        role_combo.set("Anggota")
        role_combo.pack(fill="x", ipady=6, pady=(5, 20))

        def save_new_user():
            nama = nama_entry.get().strip()
            username = username_entry.get().strip()
            email = email_entry.get().strip()
            password = password_entry.get()
            role = role_combo.get()

            if not self.validate_user_form(nama, username, email, password, window):
                return

            try:
                users = load_users()
                if username in users:
                    messagebox.showerror("Gagal", "Username sudah digunakan.", parent=window)
                    return

                success, message = register_user(nama, username, email, password)
                if not success:
                    messagebox.showerror("Gagal", message, parent=window)
                    return

                users_after = load_users()
                if username in users_after:
                    users_after[username]["role"] = role
                    users_after[username]["status"] = "Aktif"
                    save_users(users_after)

                messagebox.showinfo("Berhasil", "User berhasil ditambahkan.", parent=window)
                window.destroy()
                self.current_page = 1
                self.refresh_table()

            except Exception as e:
                messagebox.showerror("Error", f"Gagal menambahkan user:\n\n{e}", parent=window)

        tk.Button(window, text="Simpan", bg=COLOR_ACCENT, fg="white", activebackground=COLOR_ACCENT_DARK, activeforeground="white", relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 11, "bold"), command=save_new_user).pack(ipadx=35, ipady=8, pady=(10, 30))
        username_entry.focus()

    def open_edit_user(self, username):
        users = load_users()
        if username not in users:
            messagebox.showerror("Error", "User tidak ditemukan.")
            self.refresh_table()
            return

        data = users[username]
        window = tk.Toplevel(self)
        window.title("Edit User")
        window.geometry("460x680")
        window.resizable(False, False)
        window.configure(bg=self.WHITE)
        self.center_window(window, 460, 680)

        tk.Label(window, text="Edit User", bg=self.WHITE, fg=COLOR_TEXT, font=("Segoe UI", 19, "bold")).pack(pady=(25, 20))
        form = tk.Frame(window, bg=self.WHITE)
        form.pack(fill="x", padx=40)

        nama_entry = self.create_form_entry(form, "Nama Lengkap")
        nama_entry.insert(0, data.get("nama", ""))

        username_entry = self.create_form_entry(form, "Username")
        username_entry.insert(0, username)

        email_entry = self.create_form_entry(form, "Email")
        email_entry.insert(0, data.get("email", ""))

        password_entry = self.create_form_entry(form, "Password Baru", show="*")
        tk.Label(form, text="Kosongkan jika password tidak ingin diubah.", bg=self.WHITE, fg=COLOR_MUTED, font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 15))

        tk.Label(form, text="Peran", bg=self.WHITE, fg=COLOR_TEXT, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        role_combo = ttk.Combobox(form, values=["Admin", "Pustakawan", "Anggota"], state="readonly", font=("Segoe UI", 10))
        role_combo.set(data.get("role", "Anggota"))
        role_combo.pack(fill="x", ipady=6, pady=(5, 15))

        tk.Label(form, text="Status", bg=self.WHITE, fg=COLOR_TEXT, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        status_combo = ttk.Combobox(form, values=["Aktif", "Tidak Aktif"], state="readonly", font=("Segoe UI", 10))
        status_combo.set(data.get("status", "Aktif"))
        status_combo.pack(fill="x", ipady=6, pady=(5, 20))

        def save_changes():
            new_nama = nama_entry.get().strip()
            new_username = username_entry.get().strip()
            new_email = email_entry.get().strip()
            new_password = password_entry.get()
            new_role = role_combo.get()
            new_status = status_combo.get()

            if not self.validate_user_form(new_nama, new_username, new_email, None, window):
                return

            if new_password and len(new_password) < 8:
                messagebox.showwarning("Peringatan", "Password minimal 8 karakter.", parent=window)
                return

            try:
                users_now = load_users()
                if new_username != username and new_username in users_now:
                    messagebox.showerror("Gagal", "Username baru sudah digunakan.", parent=window)
                    return

                success, message = update_user(username, new_username, new_nama, new_email, new_role, new_status, new_password)
                if not success:
                    messagebox.showerror("Gagal", message, parent=window)
                    return

                if self.controller.current_user == username:
                    self.controller.set_current_user(new_username)

                messagebox.showinfo("Berhasil", "Data user berhasil diperbarui.", parent=window)
                window.destroy()
                self.refresh_table()
                self.update_current_user_label()

            except Exception as e:
                messagebox.showerror("Error", f"Gagal memperbarui user:\n\n{e}", parent=window)

        tk.Button(window, text="Simpan Perubahan", bg=COLOR_ACCENT, fg="white", activebackground=COLOR_ACCENT_DARK, activeforeground="white", relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 11, "bold"), command=save_changes).pack(ipadx=25, ipady=8, pady=(10, 30))
        username_entry.focus()

    # DELETE ACTION

    def delete_user_action(self, username):
        if self.controller.current_user == username:
            messagebox.showwarning("Tidak Diizinkan", "Akun yang sedang digunakan tidak dapat dihapus.")
            return

        users = load_users()
        if username not in users:
            messagebox.showerror("Error", "User tidak ditemukan.")
            self.refresh_table()
            return

        data = users[username]
        confirmation = messagebox.askyesno("Konfirmasi Hapus", f"Apakah kamu yakin ingin menghapus user?\n\nNama     : {data.get('nama', '-')}\nUsername : {username}")
        if not confirmation:
            return

        try:
            success, message = delete_user(username)
            if not success:
                messagebox.showerror("Gagal", message)
                return

            messagebox.showinfo("Berhasil", "User berhasil dihapus.")
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menghapus user:\n\n{e}")

    # UTILITIES / HELPER

    def create_form_entry(self, parent, label_text, show=None):
        tk.Label(parent, text=label_text, bg=self.WHITE, fg=COLOR_TEXT, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        entry = tk.Entry(parent, font=("Segoe UI", 10), relief="solid", bd=1, show=show)
        entry.pack(fill="x", ipady=7, pady=(5, 15))
        return entry

    def validate_user_form(self, nama, username, email, password, parent):
        if not nama:
            messagebox.showwarning("Peringatan", "Nama lengkap harus diisi.", parent=parent)
            return False

        if not username:
            messagebox.showwarning("Peringatan", "Username harus diisi.", parent=parent)
            return False

        if not re.match(r"^[A-Za-z0-9_.-]+$", username):
            messagebox.showwarning("Peringatan", "Username hanya boleh mengandung huruf, angka, titik, underscore, dan minus.", parent=parent)
            return False

        if not email:
            messagebox.showwarning("Peringatan", "Email harus diisi.", parent=parent)
            return False

        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            messagebox.showwarning("Peringatan", "Format email tidak valid.", parent=parent)
            return False

        if password is not None and len(password) < 8:
            messagebox.showwarning("Peringatan", "Password minimal 8 karakter.", parent=parent)
            return False

        return True

    def update_current_user_label(self):
        current_user = self.controller.current_user
        self.user_label.config(text=current_user if current_user else "Admin")

    def center_window(self, window, width, height):
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")

    def on_show(self):
        self.update_current_user_label()
        self.search_var.set("Cari nama, username, atau email")
        self.entry_search.config(fg="#999999")
        self.role_var.set("Semua Peran")
        self.current_page = 1
        self.refresh_table()