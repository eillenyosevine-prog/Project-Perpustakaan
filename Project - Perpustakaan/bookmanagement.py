import tkinter as tk
from tkinter import ttk, messagebox

from config import (
    COLOR_PRIMARY, COLOR_ACCENT, COLOR_ACCENT_DARK, COLOR_TEXT, 
    COLOR_MUTED, COLOR_SUCCESS, COLOR_DANGER, HoverButton, 
    load_books, add_book, update_book, delete_book
)


class BookManagementPage(tk.Frame):
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
        self.category_var = tk.StringVar(value="Semua Kategori")
        self.current_page = 1
        self.filtered_books = []

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
        self.create_menu_button(menu_frame, "📖  Kelola Buku", True, lambda: self.controller.show_frame("BookManagementPage"))
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

        tk.Label(header, text="Kelola Buku", bg=self.BG, fg="#222222", font=("Segoe UI", 22, "bold")).pack(side="left", pady=20)

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
        self.entry_search.insert(0, "Cari judul, penulis, kategori")
        self.entry_search.config(fg="#999999")
        self.entry_search.bind("<FocusIn>", self.clear_placeholder)
        self.entry_search.bind("<FocusOut>", self.restore_placeholder)
        self.entry_search.bind("<KeyRelease>", self.on_search)

        self.category_combo = ttk.Combobox(top_bar, textvariable=self.category_var, values=["Semua Kategori", "Fiksi", "Pengembangan Diri", "Sejarah", "Teknologi", "Sains"], state="readonly", font=("Segoe UI", 10), width=18)
        self.category_combo.pack(side="left", padx=(0, 12), ipady=7)
        self.category_combo.bind("<<ComboboxSelected>>", self.on_filter)

        tk.Button(top_bar, text="+ Tambah Buku", bg=self.BLUE, fg="white", activebackground=self.DARK_BLUE, activeforeground="white",
                  font=("Segoe UI", 11, "bold"), relief="flat", bd=0, cursor="hand2", command=self.open_add_book).pack(side="right", ipadx=16, ipady=9)

        # Table Container Card
        self.table_card = tk.Frame(self.content, bg=self.WHITE, highlightbackground="#c9cdd1", highlightthickness=1)
        self.table_card.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        # Table Header
        self.table_header = tk.Frame(self.table_card, bg=self.HEADER_BG, height=50)
        self.table_header.pack(fill="x")
        self.table_header.pack_propagate(False)

        columns = [("No", 55), ("Judul", 210), ("Penulis", 170), ("Kategori", 150), ("Stok", 150), ("Aksi", 110)]
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
        if self.search_var.get() == "Cari judul, penulis, kategori":
            self.search_var.set("")
            self.entry_search.config(fg="#555555")

    def restore_placeholder(self, event=None):
        if not self.search_var.get().strip():
            self.search_var.set("Cari judul, penulis, kategori")
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
            books = load_books()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membaca data buku:\n\n{e}")
            return

        search_text = self.search_var.get().strip().lower()
        if search_text == "cari judul, penulis, kategori":
            search_text = ""

        selected_category = self.category_var.get()
        self.filtered_books = []

        for book in books:
            if not isinstance(book, dict):
                continue

            judul = str(book.get("judul", "-"))
            penulis = str(book.get("penulis", "-"))
            kategori = str(book.get("kategori", "Umum"))

            target = f"{judul} {penulis} {kategori}".lower()

            if search_text and search_text not in target:
                continue
            if selected_category != "Semua Kategori" and kategori not in selected_category:
                continue

            self.filtered_books.append(book)

        total_data = len(self.filtered_books)
        total_pages = max(1, (total_data + self.PER_PAGE - 1) // self.PER_PAGE)

        if self.current_page > total_pages:
            self.current_page = total_pages

        start_index = (self.current_page - 1) * self.PER_PAGE
        end_index = min(start_index + self.PER_PAGE, total_data)
        page_data = self.filtered_books[start_index:end_index]

        if not page_data:
            empty_frame = tk.Frame(self.rows_frame, bg=self.WHITE, height=100)
            empty_frame.pack(fill="x")
            empty_frame.pack_propagate(False)
            tk.Label(empty_frame, text="Tidak ada data buku.", bg=self.WHITE, fg=COLOR_MUTED, font=("Segoe UI", 11)).pack(expand=True)
        else:
            for index, book in enumerate(page_data):
                actual_number = start_index + index + 1
                self.create_book_row(actual_number, book)

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

    def create_book_row(self, number, book):
        book_id = book.get("id")
        judul = book.get("judul", "-")
        penulis = book.get("penulis", "-")
        kategori = book.get("kategori", "Umum")
        stok = book.get("stok", 0)

        row = tk.Frame(self.rows_frame, bg=self.WHITE, height=self.ROW_HEIGHT)
        row.pack(fill="x")
        row.pack_propagate(False)

        widths = [55, 210, 170, 150, 150, 110]

        # No
        self.create_cell(row, str(number), widths[0], anchor="center")

        # Judul
        self.create_cell(row, judul, widths[1], anchor="w")

        # Penulis
        self.create_cell(row, penulis, widths[2], anchor="w")

        # Kategori
        self.create_cell(row, kategori, widths[3], anchor="center")

        # Stok (Tersedia)
        stok_frame = tk.Frame(row, bg=self.WHITE, width=widths[4])
        stok_frame.pack(side="left", fill="y")
        stok_frame.pack_propagate(False)

        stok_container = tk.Frame(stok_frame, bg=self.WHITE)
        stok_container.pack(expand=True, anchor="center")

        tk.Label(stok_container, text=f"Tersedia  : {stok}", bg=self.WHITE, fg=COLOR_TEXT, font=("Segoe UI", 9)).pack(anchor="w")

        # Aksi
        action_frame = tk.Frame(row, bg=self.WHITE, width=widths[5])
        action_frame.pack(side="left", fill="y")
        action_frame.pack_propagate(False)

        action_container = tk.Frame(action_frame, bg=self.WHITE)
        action_container.pack(expand=True)

        tk.Button(action_container, text="✏️", bg=self.YELLOW, fg="#333333", activebackground="#e5c331", relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 10), width=3, height=1, command=lambda b=book_id: self.open_edit_book(b)).pack(side="left", padx=3)
        tk.Button(action_container, text="    🗑️", bg="#f5b7b1", fg=self.RED, activebackground="#ec7063", relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 10), width=3, height=1, command=lambda b=book_id: self.delete_book_action(b)).pack(side="left", padx=3)

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
        total_data = len(self.filtered_books)
        total_pages = max(1, (total_data + self.PER_PAGE - 1) // self.PER_PAGE)
        if self.current_page < total_pages:
            self.current_page += 1
            self.refresh_table()

    def update_scroll_region(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def resize_canvas_window(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    # TAMBAH & EDIT BUKU

    def open_add_book(self):
        window = tk.Toplevel(self)
        window.title("Tambah Buku")
        window.geometry("460x600")
        window.resizable(False, False)
        window.configure(bg=self.WHITE)
        self.center_window(window, 460, 600)

        tk.Label(window, text="Tambah Buku", bg=self.WHITE, fg=COLOR_TEXT, font=("Segoe UI", 19, "bold")).pack(pady=(25, 20))
        form = tk.Frame(window, bg=self.WHITE)
        form.pack(fill="x", padx=40)

        judul_entry = self.create_form_entry(form, "Judul Buku")
        penulis_entry = self.create_form_entry(form, "Penulis")

        tk.Label(form, text="Kategori", bg=self.WHITE, fg=COLOR_TEXT, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        kategori_combo = ttk.Combobox(form, values=["Fiksi", "Pengembangan Diri", "Sejarah", "Teknologi", "Sains"], state="readonly", font=("Segoe UI", 10))
        kategori_combo.set("Fiksi")
        kategori_combo.pack(fill="x", ipady=6, pady=(5, 15))

        stok_entry = self.create_form_entry(form, "Jumlah Stok Tersedia")

        def save_new_book():
            judul = judul_entry.get().strip()
            penulis = penulis_entry.get().strip()
            kategori = kategori_combo.get()
            stok_text = stok_entry.get().strip()

            if not judul or not penulis or not stok_text:
                messagebox.showwarning("Peringatan", "Semua field wajib diisi.", parent=window)
                return

            try:
                stok = int(stok_text)
                if stok < 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Peringatan", "Stok harus berupa angka bulat >= 0.", parent=window)
                return

            try:
                success, message = add_book(judul, penulis, kategori, stok)
                if not success:
                    messagebox.showerror("Gagal", message, parent=window)
                    return

                messagebox.showinfo("Berhasil", "Buku berhasil ditambahkan.", parent=window)
                window.destroy()
                self.current_page = 1
                self.refresh_table()

            except Exception as e:
                messagebox.showerror("Error", f"Gagal menambahkan buku:\n\n{e}", parent=window)

        tk.Button(window, text="Simpan", bg=COLOR_ACCENT, fg="white", activebackground=COLOR_ACCENT_DARK, activeforeground="white", relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 11, "bold"), command=save_new_book).pack(ipadx=35, ipady=8, pady=(10, 30))
        judul_entry.focus()

    def open_edit_book(self, book_id):
        books = load_books()
        target_book = next((b for b in books if b.get("id") == book_id), None)

        if not target_book:
            messagebox.showerror("Error", "Buku tidak ditemukan.")
            self.refresh_table()
            return

        window = tk.Toplevel(self)
        window.title("Edit Buku")
        window.geometry("460x600")
        window.resizable(False, False)
        window.configure(bg=self.WHITE)
        self.center_window(window, 460, 600)

        tk.Label(window, text="Edit Buku", bg=self.WHITE, fg=COLOR_TEXT, font=("Segoe UI", 19, "bold")).pack(pady=(25, 20))
        form = tk.Frame(window, bg=self.WHITE)
        form.pack(fill="x", padx=40)

        judul_entry = self.create_form_entry(form, "Judul Buku")
        judul_entry.insert(0, target_book.get("judul", ""))

        penulis_entry = self.create_form_entry(form, "Penulis")
        penulis_entry.insert(0, target_book.get("penulis", ""))

        tk.Label(form, text="Kategori", bg=self.WHITE, fg=COLOR_TEXT, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        kategori_combo = ttk.Combobox(form, values=["Fiksi", "Pengembangan Diri", "Sejarah", "Teknologi", "Sains"], state="readonly", font=("Segoe UI", 10))
        kategori_combo.set(target_book.get("kategori", "Fiksi"))
        kategori_combo.pack(fill="x", ipady=6, pady=(5, 15))

        stok_entry = self.create_form_entry(form, "Jumlah Stok Tersedia")
        stok_entry.insert(0, str(target_book.get("stok", 0)))

        def save_changes():
            new_judul = judul_entry.get().strip()
            new_penulis = penulis_entry.get().strip()
            new_kategori = kategori_combo.get()
            stok_text = stok_entry.get().strip()

            if not new_judul or not new_penulis or not stok_text:
                messagebox.showwarning("Peringatan", "Semua field wajib diisi.", parent=window)
                return

            try:
                new_stok = int(stok_text)
                if new_stok < 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Peringatan", "Stok harus berupa angka bulat >= 0.", parent=window)
                return

            try:
                success, message = update_book(book_id, new_judul, new_penulis, new_kategori, new_stok)
                if not success:
                    messagebox.showerror("Gagal", message, parent=window)
                    return

                messagebox.showinfo("Berhasil", "Data buku berhasil diperbarui.", parent=window)
                window.destroy()
                self.refresh_table()

            except Exception as e:
                messagebox.showerror("Error", f"Gagal memperbarui buku:\n\n{e}", parent=window)

        tk.Button(window, text="Simpan Perubahan", bg=COLOR_ACCENT, fg="white", activebackground=COLOR_ACCENT_DARK, activeforeground="white", relief="flat", bd=0, cursor="hand2", font=("Segoe UI", 11, "bold"), command=save_changes).pack(ipadx=25, ipady=8, pady=(10, 30))
        judul_entry.focus()

    # HAPUS BUKU

    def delete_book_action(self, book_id):
        books = load_books()
        target_book = next((b for b in books if b.get("id") == book_id), None)

        if not target_book:
            messagebox.showerror("Error", "Buku tidak ditemukan.")
            self.refresh_table()
            return

        confirmation = messagebox.askyesno("Konfirmasi Hapus", f"Apakah kamu yakin ingin menghapus buku?\n\nJudul   : {target_book.get('judul', '-')}\nPenulis : {target_book.get('penulis', '-')}")
        if not confirmation:
            return

        try:
            success, message = delete_book(book_id)
            if not success:
                messagebox.showerror("Gagal", message)
                return

            messagebox.showinfo("Berhasil", "Buku berhasil dihapus.")
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menghapus buku:\n\n{e}")

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
        self.search_var.set("Cari judul, penulis, kategori")
        self.entry_search.config(fg="#999999")
        self.category_var.set("Semua Kategori")
        self.current_page = 1
        self.refresh_table()