import tkinter as tk
from tkinter import ttk, messagebox

from config import (
    COLOR_PRIMARY, COLOR_ACCENT, COLOR_ACCENT_DARK, COLOR_TEXT, 
    COLOR_MUTED, COLOR_SUCCESS, COLOR_DANGER, HoverButton, 
    load_books, load_borrowings, add_borrowing, update_borrowing, delete_borrowing
)


class BorrowingManagementPage(tk.Frame):
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
        self.date_filter_var = tk.StringVar(value="Semua Tanggal")
        self.current_page = 1
        self.filtered_borrowings = []

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
        self.create_menu_button(menu_frame, "👥  Kelola User", False, lambda: self.controller.show_frame("UsersManagementPage"))
        self.create_menu_button(menu_frame, "📖  Kelola Buku", False, lambda: self.controller.show_frame("BookManagementPage"))
        self.create_menu_button(menu_frame, "🔄  Kelola Peminjaman", True, lambda: self.controller.show_frame("BorrowingManagementPage"))

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

        tk.Label(header, text="Kelola Peminjaman", bg=self.BG, fg="#222222", font=("Segoe UI", 22, "bold")).pack(side="left", pady=20)

        user_frame = tk.Frame(header, bg=self.BG)
        user_frame.pack(side="right", pady=15)
        tk.Label(user_frame, text="👤", bg=self.BG, fg="#2c3e50", font=("Segoe UI", 16)).pack(side="left", padx=(0, 6))

        self.user_label = tk.Label(user_frame, text="Admin", bg=self.BG, fg=COLOR_TEXT, font=("Segoe UI", 12, "bold"))
        self.user_label.pack(side="left")

        tk.Frame(self.content, bg="#bfc3c7", height=1).pack(fill="x", padx=30)

        # Top Bar (Filter, Search, Button)
        top_bar = tk.Frame(self.content, bg=self.BG)
        top_bar.pack(fill="x", padx=30, pady=(25, 18))

        search_frame = tk.Frame(top_bar, bg=self.WHITE, highlightbackground="#bfc3c7", highlightthickness=1)
        search_frame.pack(side="left", fill="x", expand=True, padx=(0, 12))

        tk.Label(search_frame, text="🔍︎", bg=self.WHITE, fg="#777777", font=("Segoe UI", 11)).pack(side="left", padx=(10, 5))

        self.entry_search = tk.Entry(search_frame, textvariable=self.search_var, bg=self.WHITE, fg="#555555", relief="flat", bd=0, font=("Segoe UI", 11))
        self.entry_search.pack(side="left", fill="x", expand=True, ipady=9)
        self.entry_search.insert(0, "Cari username, judul buku")
        self.entry_search.config(fg="#999999")
        self.entry_search.bind("<FocusIn>", self.clear_placeholder)
        self.entry_search.bind("<FocusOut>", self.restore_placeholder)
        self.entry_search.bind("<KeyRelease>", self.on_search)

        self.date_combo = ttk.Combobox(top_bar, textvariable=self.date_filter_var, values=["Semua Tanggal", "Hari Ini", "Bulan Ini"], state="readonly", font=("Segoe UI", 10), width=18)
        self.date_combo.pack(side="left", padx=(0, 12), ipady=7)
        self.date_combo.bind("<<ComboboxSelected>>", self.on_filter)

        tk.Button(top_bar, text="+ Peminjaman Baru", bg=self.BLUE, fg="white", activebackground=self.DARK_BLUE, activeforeground="white",
                  font=("Segoe UI", 11, "bold"), relief="flat", bd=0, cursor="hand2", command=self.open_add_borrowing).pack(side="right", ipadx=16, ipady=9)

        # Table Container Card
        self.table_card = tk.Frame(self.content, bg=self.WHITE, highlightbackground="#c9cdd1", highlightthickness=1)
        self.table_card.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        # Table Header
        self.table_header = tk.Frame(self.table_card, bg=self.HEADER_BG, height=50)
        self.table_header.pack(fill="x")
        self.table_header.pack_propagate(False)

        columns = [("No", 50), ("Username", 150), ("Judul Buku", 190), ("Tanggal Pinjam", 130), ("Tanggal Kembali", 130), ("Status", 110), ("Aksi", 110)]
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

    # PLACEHOLDER & FILTER HANDLER

    def clear_placeholder(self, event=None):
        if self.search_var.get() == "Cari username, judul buku":
            self.search_var.set("")
            self.entry_search.config(fg="#555555")

    def restore_placeholder(self, event=None):
        if not self.search_var.get().strip():
            self.search_var.set("Cari username, judul buku")
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
            borrowings = load_borrowings()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membaca data peminjaman:\n\n{e}")
            return

        search_text = self.search_var.get().strip().lower()
        if search_text == "cari username, judul buku":
            search_text = ""

        self.filtered_borrowings = []

        for item in borrowings:
            if not isinstance(item, dict):
                continue

            nama = str(item.get("nama", item.get("username", "-")))
            judul = str(item.get("judul", "-"))

            target = f"{nama} {judul}".lower()

            if search_text and search_text not in target:
                continue

            self.filtered_borrowings.append(item)

        total_data = len(self.filtered_borrowings)
        total_pages = max(1, (total_data + self.PER_PAGE - 1) // self.PER_PAGE)

        if self.current_page > total_pages:
            self.current_page = total_pages

        start_index = (self.current_page - 1) * self.PER_PAGE
        end_index = min(start_index + self.PER_PAGE, total_data)
        page_data = self.filtered_borrowings[start_index:end_index]

        if not page_data:
            empty_frame = tk.Frame(self.rows_frame, bg=self.WHITE, height=100)
            empty_frame.pack(fill="x")
            empty_frame.pack_propagate(False)
            tk.Label(empty_frame, text="Tidak ada data peminjaman.", bg=self.WHITE, fg=COLOR_MUTED, font=("Segoe UI", 11)).pack(expand=True)
        else:
            for index, data in enumerate(page_data):
                actual_number = start_index + index + 1
                self.create_borrowing_row(actual_number, data)

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

    def create_borrowing_row(self, number, data):
        b_id = data.get("id")
        nama = data.get("nama", data.get("username", "-"))
        judul = data.get("judul", "-")
        tgl_pinjam = data.get("tanggal_pinjam", "-")
        tgl_kembali = data.get("tanggal_kembali", "-")
        status = data.get("status", "Dipinjam")

        row = tk.Frame(self.rows_frame, bg=self.WHITE, height=self.ROW_HEIGHT)
        row.pack(fill="x")
        row.pack_propagate(False)

        widths = [50, 150, 190, 130, 130, 110, 110]

        # No
        self.create_cell(row, str(number), widths[0], anchor="center")

        # Username
        self.create_cell(row, nama, widths[1], anchor="w")

        # Judul Buku
        self.create_cell(row, judul, widths[2], anchor="w")

        # Tanggal Pinjam
        self.create_cell(row, tgl_pinjam, widths[3], anchor="center")

        # Tanggal Kembali
        self.create_cell(row, tgl_kembali if tgl_kembali else "-", widths[4], anchor="center")

        # Status
        status_frame = tk.Frame(row, bg=self.WHITE, width=widths[5])
        status_frame.pack(side="left", fill="y")
        status_frame.pack_propagate(False)
        status_color = self.GREEN if status == "Dikembalikan" else self.YELLOW
        fg_color = "white" if status == "Dikembalikan" else "#333333"
        tk.Label(status_frame, text=status, bg=status_color, fg=fg_color, font=("Segoe UI", 8, "bold"), padx=8).pack(padx=8, pady=17)

        # Aksi
        action_frame = tk.Frame(row, bg=self.WHITE, width=widths[6])
        action_frame.pack(side="left", fill="y")
        action_frame.pack_propagate(False)

        action_container = tk.Frame(action_frame, bg=self.WHITE)
        action_container.pack(expand=True)

        tk.Button(action_container, text="    👁️", bg="#e0e0e0", fg="#333333", activebackground="#cccccc", relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 10), width=3, height=1, command=lambda b=b_id: self.open_detail_borrowing(b)).pack(side="left", padx=3)
        tk.Button(action_container, text="✏️", bg=self.YELLOW, fg="#333333", activebackground="#e5c331", relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 10), width=3, height=1, command=lambda b=b_id: self.open_edit_borrowing(b)).pack(side="left", padx=3)

        tk.Frame(self.rows_frame, bg=self.BORDER, height=1).pack(fill="x")

    def create_cell(self, parent, text, width, anchor="w"):
        frame = tk.Frame(parent, bg=self.WHITE, width=width)
        frame.pack(side="left", fill="y")
        frame.pack_propagate(False)
        tk.Label(frame, text=text, bg=self.WHITE, fg=COLOR_TEXT, font=("Segoe UI", 10), anchor=anchor, wraplength=width-10).pack(fill="both", expand=True, padx=8)

    # PAGINATION & SCROLLING

    def previous_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.refresh_table()

    def next_page(self):
        total_data = len(self.filtered_borrowings)
        total_pages = max(1, (total_data + self.PER_PAGE - 1) // self.PER_PAGE)
        if self.current_page < total_pages:
            self.current_page += 1
            self.refresh_table()

    def update_scroll_region(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def resize_canvas_window(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)


    # TAMBAH, EDIT & DETAIL PEMINJAMAN

    def open_add_borrowing(self):
        window = tk.Toplevel(self)
        window.title("Tambah Peminjaman Baru")
        window.geometry("460x600")
        window.resizable(False, False)
        window.configure(bg=self.WHITE)
        self.center_window(window, 460, 600)

        tk.Label(window, text="Peminjaman Baru", bg=self.WHITE, fg=COLOR_TEXT, font=("Segoe UI", 19, "bold")).pack(pady=(25, 20))
        form = tk.Frame(window, bg=self.WHITE)
        form.pack(fill="x", padx=40)

        nama_entry = self.create_form_entry(form, "Username")

        # Load Pilihan Buku
        books = load_books()
        book_options = [f"{b.get('id')} - {b.get('judul')}" for b in books]

        tk.Label(form, text="Pilih Buku", bg=self.WHITE, fg=COLOR_TEXT, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        book_combo = ttk.Combobox(form, values=book_options, state="readonly", font=("Segoe UI", 10))
        if book_options:
            book_combo.set(book_options[0])
        book_combo.pack(fill="x", ipady=6, pady=(5, 15))

        tgl_pinjam_entry = self.create_form_entry(form, "Tanggal Pinjam (misal: 28 Ags 2026)")

        def save_new_borrowing():
            nama = nama_entry.get().strip()
            selected_book = book_combo.get()
            tgl_pinjam = tgl_pinjam_entry.get().strip()

            if not nama or not selected_book or not tgl_pinjam:
                messagebox.showwarning("Peringatan", "Semua field wajib diisi.", parent=window)
                return

            try:
                book_id = int(selected_book.split(" - ")[0])
                success, message = add_borrowing(nama, book_id, tgl_pinjam, "-")
                if not success:
                    messagebox.showerror("Gagal", message, parent=window)
                    return

                messagebox.showinfo("Berhasil", "Data peminjaman berhasil ditambahkan.", parent=window)
                window.destroy()
                self.current_page = 1
                self.refresh_table()

            except Exception as e:
                messagebox.showerror("Error", f"Gagal menambahkan peminjaman:\n\n{e}", parent=window)

        tk.Button(window, text="Simpan", bg=COLOR_ACCENT, fg="white", activebackground=COLOR_ACCENT_DARK, activeforeground="white", relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 11, "bold"), command=save_new_borrowing).pack(ipadx=35, ipady=8, pady=(10, 30))
        nama_entry.focus()

    def open_edit_borrowing(self, b_id):
        borrowings = load_borrowings()
        target = next((item for item in borrowings if item.get("id") == b_id), None)

        if not target:
            messagebox.showerror("Error", "Data peminjaman tidak ditemukan.")
            self.refresh_table()
            return

        window = tk.Toplevel(self)
        window.title("Edit Peminjaman")
        window.geometry("460x620")
        window.resizable(False, False)
        window.configure(bg=self.WHITE)
        self.center_window(window, 460, 620)

        tk.Label(window, text="Edit Peminjaman", bg=self.WHITE, fg=COLOR_TEXT, font=("Segoe UI", 19, "bold")).pack(pady=(25, 20))
        form = tk.Frame(window, bg=self.WHITE)
        form.pack(fill="x", padx=40)

        nama_entry = self.create_form_entry(form, "Username")
        nama_entry.insert(0, target.get("nama", target.get("username", "")))

        tgl_pinjam_entry = self.create_form_entry(form, "Tanggal Pinjam")
        tgl_pinjam_entry.insert(0, target.get("tanggal_pinjam", ""))

        tgl_kembali_entry = self.create_form_entry(form, "Tanggal Kembali")
        tgl_kembali_entry.insert(0, target.get("tanggal_kembali", ""))

        tk.Label(form, text="Status", bg=self.WHITE, fg=COLOR_TEXT, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        status_combo = ttk.Combobox(form, values=["Dipinjam", "Dikembalikan"], state="readonly", font=("Segoe UI", 10))
        status_combo.set(target.get("status", "Dipinjam"))
        status_combo.pack(fill="x", ipady=6, pady=(5, 20))

        def save_changes():
            new_nama = nama_entry.get().strip()
            new_pinjam = tgl_pinjam_entry.get().strip()
            new_kembali = tgl_kembali_entry.get().strip()
            new_status = status_combo.get()

            try:
                success, message = update_borrowing(b_id, new_nama, target.get("book_id"), new_pinjam, new_kembali, new_status)
                if not success:
                    messagebox.showerror("Gagal", message, parent=window)
                    return

                messagebox.showinfo("Berhasil", "Data peminjaman diperbarui.", parent=window)
                window.destroy()
                self.refresh_table()

            except Exception as e:
                messagebox.showerror("Error", f"Gagal memperbarui peminjaman:\n\n{e}", parent=window)

        tk.Button(window, text="Simpan Perubahan", bg=COLOR_ACCENT, fg="white", activebackground=COLOR_ACCENT_DARK, activeforeground="white", relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 11, "bold"), command=save_changes).pack(ipadx=25, ipady=8, pady=(10, 30))

    def open_detail_borrowing(self, b_id):
        borrowings = load_borrowings()
        target = next((item for item in borrowings if item.get("id") == b_id), None)

        if not target:
            messagebox.showerror("Error", "Data peminjaman tidak ditemukan.")
            return

        window = tk.Toplevel(self)
        window.title("Detail Peminjaman")
        window.geometry("400x380")
        window.resizable(False, False)
        window.configure(bg=self.WHITE)
        self.center_window(window, 400, 380)

        tk.Label(window, text="Detail Peminjaman", bg=self.WHITE, fg=COLOR_TEXT, font=("Segoe UI", 16, "bold")).pack(pady=(20, 15))

        details_frame = tk.Frame(window, bg=self.WHITE)
        details_frame.pack(fill="both", expand=True, padx=30)

        info = [
            ("Username", target.get("nama", target.get("username", "-"))),
            ("Judul Buku", target.get("judul", "-")),
            ("Tanggal Pinjam", target.get("tanggal_pinjam", "-")),
            ("Tanggal Kembali", target.get("tanggal_kembali", "-")),
            ("Status", target.get("status", "-"))
        ]

        for label, val in info:
            f = tk.Frame(details_frame, bg=self.WHITE)
            f.pack(fill="x", pady=4)
            tk.Label(f, text=f"{label}:", bg=self.WHITE, fg=COLOR_MUTED, font=("Segoe UI", 10, "bold"), width=15, anchor="w").pack(side="left")
            tk.Label(f, text=val, bg=self.WHITE, fg=COLOR_TEXT, font=("Segoe UI", 10), anchor="w").pack(side="left", fill="x", expand=True)

        tk.Button(window, text="Tutup", bg=self.BLUE, fg="white", relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 10, "bold"), command=window.destroy).pack(ipadx=20, ipady=6, pady=20)

    # UTILITIES / HELPER

    def create_form_entry(self, parent, label_text):
        tk.Label(parent, text=label_text, bg=self.WHITE, fg=COLOR_TEXT, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        entry = tk.Entry(parent, font=("Segoe UI", 10), relief="solid", bd=1)
        entry.pack(fill="x", ipady=7, pady=(5, 15))
        return entry

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
        self.search_var.set("Cari username, judul buku")
        self.entry_search.config(fg="#999999")
        self.date_filter_var.set("Semua Tanggal")
        self.current_page = 1
        self.refresh_table()