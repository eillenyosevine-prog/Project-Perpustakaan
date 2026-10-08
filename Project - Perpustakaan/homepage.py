import tkinter as tk
from config import (
    COLOR_PRIMARY, COLOR_ACCENT, COLOR_ACCENT_DARK, COLOR_BG, COLOR_CARD,
    COLOR_TEXT, COLOR_MUTED, FONT_TITLE, FONT_SUBTITLE, FONT_NAV,
    FONT_CARD_TITLE, FONT_CARD_BODY, ARTIKEL_PERPUSTAKAAN, HoverButton,
)


class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#b7d4ff")
        self.controller = controller

        self.WHITE = "#ffffff"
        self.BG = "#dceaff"
        self.ACTIVE_BLUE = "#b9dcf5"
        self.RED = "#d93025"

        self.build_sidebar()
        self.build_content()

    # SIDEBAR

    def build_sidebar(self):
        self.sidebar = tk.Frame(self, bg=self.WHITE, width=260, highlightbackground="#d0d0d0", highlightthickness=1)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Frame Logo Header Sidebar
        logo_frame = tk.Frame(self.sidebar, bg=COLOR_PRIMARY, height=100)
        logo_frame.pack(fill="x")
        logo_frame.pack_propagate(False)

        tk.Label(logo_frame, text="📚 PerpustakaanKu", bg=COLOR_PRIMARY, fg="white", font=("Segoe UI", 17, "bold")).pack(expand=True)

        self.menu_frame = tk.Frame(self.sidebar, bg=self.WHITE)
        self.menu_frame.pack(fill="both", expand=True)

        self.render_menu()

    def render_menu(self):
        """Memperbarui tombol menu navigasi berdasarkan status login pengguna"""
        for widget in self.menu_frame.winfo_children():
            widget.destroy()

        is_logged_in = hasattr(self.controller, 'current_user') and self.controller.current_user

        if is_logged_in:
            self.create_menu_button(self.menu_frame, "🏠  Beranda", True, lambda: self.controller.show_frame("HomePage"))
            self.create_menu_button(self.menu_frame, "👥  Kelola User", False, lambda: self.controller.show_frame("UsersManagementPage"))
            self.create_menu_button(self.menu_frame, "📖  Kelola Buku", False, lambda: self.controller.show_frame("BookManagementPage"))
            self.create_menu_button(self.menu_frame, "🔄  Kelola Peminjaman", False, lambda: self.controller.show_frame("BorrowingManagementPage"))

            tk.Frame(self.menu_frame, bg=self.WHITE).pack(fill="both", expand=True)
            self.create_menu_button(self.menu_frame, "➜]  Logout", False, self.controller.logout, danger=True)
        else:
            self.create_menu_button(self.menu_frame, "🔑  Login", False, lambda: self.controller.show_frame("SignInPage"))
            self.create_menu_button(self.menu_frame, "📝  Daftar", False, lambda: self.controller.show_frame("SignUpPage"))

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

        tk.Label(header, text="Beranda", bg=self.BG, fg="#222222", font=("Segoe UI", 22, "bold")).pack(side="left", pady=20)

        user_frame = tk.Frame(header, bg=self.BG)
        user_frame.pack(side="right", pady=15)
        tk.Label(user_frame, text="👤", bg=self.BG, fg="#2c3e50", font=("Segoe UI", 16)).pack(side="left", padx=(0, 6))

        self.user_label = tk.Label(user_frame, text="Tamu", bg=self.BG, fg=COLOR_TEXT, font=("Segoe UI", 12, "bold"))
        self.user_label.pack(side="left")

        tk.Frame(self.content, bg="#bfc3c7", height=1).pack(fill="x", padx=30)

        # FOOTER HAK CIPTA

        footer = tk.Frame(self.content, bg=COLOR_PRIMARY, height=18)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        tk.Label(
            footer, text="© 2026 PerpustakaanKu — Semua hak cipta dilindungi.",
            bg=COLOR_PRIMARY, fg="#bdc3c7", font=("Segoe UI", 7)
        ).pack(pady=5)

        # FRAME BODY KONTEN

        body_frame = tk.Frame(self.content, bg=self.BG, padx=30, pady=20)
        body_frame.pack(fill="both", expand=True)

        # Hero Banner
        hero_card = tk.Frame(body_frame, bg="white", bd=1, relief="solid", padx=30, pady=25)
        hero_card.pack(fill="x", pady=(0, 25))

        tk.Label(
            hero_card, text="Selamat Datang di PerpustakaanKu!",
            bg="white", fg=COLOR_TEXT, font=FONT_TITLE
        ).pack(anchor="w")

        tk.Label(
            hero_card,
            text="Temukan buku favoritmu, perluas wawasanmu, raih masa depan yang lebih baik.",
            bg="white", fg=COLOR_MUTED, font=FONT_SUBTITLE
        ).pack(anchor="w", pady=(5, 15))

        # Bar Pencarian
        search_frame = tk.Frame(hero_card, bg="white")
        search_frame.pack(fill="x")

        self.search_entry = tk.Entry(
            search_frame, font=("Segoe UI", 10), bd=1, relief="solid", fg="gray"
        )
        self.search_entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 5))
        self.search_entry.insert(0, "Cari judul buku, penulis, atau kategori...")
        self.search_entry.bind("<FocusIn>", self._clear_placeholder)
        self.search_entry.bind("<FocusOut>", self._add_placeholder)

        search_btn = HoverButton(
            search_frame, text="🔍", bg_normal=COLOR_ACCENT, bg_hover=COLOR_ACCENT_DARK,
            fg="white", font=("Segoe UI", 10, "bold"), bd=0, width=5, pady=4,
            cursor="hand2", command=self._on_search
        )
        search_btn.pack(side="left")

        # Section Artikel Terbaru
        article_header = tk.Frame(body_frame, bg=self.BG)
        article_header.pack(fill="x", pady=(0, 10))

        tk.Label(
            article_header, text="Artikel Terbaru",
            bg=self.BG, fg=COLOR_TEXT, font=("Segoe UI", 14, "bold")
        ).pack(side="left")

        see_all_lbl = tk.Label(
            article_header, text="Lihat semua ➔",
            bg=self.BG, fg=COLOR_ACCENT, font=("Segoe UI", 10, "bold"), cursor="hand2"
        )
        see_all_lbl.pack(side="right")
        see_all_lbl.bind("<Button-1>", lambda e: self._on_see_all())

        cards_container = tk.Frame(body_frame, bg=self.BG)
        cards_container.pack(fill="x")

        for idx, artikel in enumerate(ARTIKEL_PERPUSTAKAAN[:4]):
            cards_container.columnconfigure(idx, weight=1)
            self._build_article_card(cards_container, artikel, idx)

    def _build_article_card(self, parent, artikel, col):
        card = tk.Frame(parent, bg="white", bd=1, relief="solid", padx=10, pady=10)
        card.grid(row=0, column=col, padx=8, sticky="nsew")

        img_placeholder = tk.Frame(card, bg="#34495e", height=80)
        img_placeholder.pack(fill="x", pady=(0, 8))
        img_placeholder.pack_propagate(False)

        tk.Label(
            img_placeholder, text="🖼️", bg="#34495e", fg="white", font=("Segoe UI", 20)
        ).pack(expand=True)

        tk.Label(
            card, text=artikel.get("judul", ""), bg="white", fg=COLOR_TEXT,
            font=FONT_CARD_TITLE, wraplength=160, justify="left"
        ).pack(anchor="w")

        tk.Label(
            card, text=artikel.get("tanggal", "12 Sep 2026"), bg="white", fg=COLOR_MUTED,
            font=("Segoe UI", 8)
        ).pack(anchor="w", pady=(2, 6))

        tk.Label(
            card, text=artikel.get("ringkasan", ""), bg="white", fg=COLOR_MUTED,
            font=FONT_CARD_BODY, wraplength=160, justify="left"
        ).pack(anchor="w")

    def _clear_placeholder(self, event):
        if self.search_entry.get() == "Cari judul buku, penulis, atau kategori...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg="black")

    def _add_placeholder(self, event):
        if not self.search_entry.get().strip():
            self.search_entry.insert(0, "Cari judul buku, penulis, atau kategori...")
            self.search_entry.config(fg="gray")

    def _on_search(self):
        pass

    def _on_see_all(self):
        pass

    def on_show(self):
        """Otomatis memilah tampilan menu navigasi dan nama user di header setiap kali halaman ditampilkan"""
        self.render_menu()
        if hasattr(self.controller, 'current_user') and self.controller.current_user:
            self.user_label.config(text=str(self.controller.current_user))
        else:
            self.user_label.config(text="Tamu")