import tkinter as tk
import json
import os
import hashlib


APP_WIDTH = 1280
APP_HEIGHT = 720

USERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json")
BOOKS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "books.json")
BORROWINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "borrowings.json")


COLOR_PRIMARY = "#2c3e50"
COLOR_ACCENT = "#2980b9"
COLOR_ACCENT_DARK = "#1c5980"
COLOR_BG = "#7ad7ff"
COLOR_CARD = "#ffffff"
COLOR_TEXT = "#2c3e50"
COLOR_MUTED = "#7f8c8d"
COLOR_SUCCESS = "#27ae60"
COLOR_DANGER = "#c0392b"


FONT_TITLE = ("Segoe UI", 26, "bold")
FONT_SUBTITLE = ("Segoe UI", 12)
FONT_NAV = ("Segoe UI", 11, "bold")
FONT_CARD_TITLE = ("Segoe UI", 14, "bold")
FONT_CARD_BODY = ("Segoe UI", 10)
FONT_LABEL = ("Segoe UI", 11)
FONT_BUTTON = ("Segoe UI", 11, "bold")


ARTIKEL_PERPUSTAKAAN = [
    {
        "judul": "5 Rekomendasi Buku Fiksi Bulan Ini",
        "ringkasan": "Temukan lima judul fiksi terbaru yang tersedia di rak perpustakaan "
                     "kami, mulai dari novel misteri hingga fantasi epik.",
        "kategori": "Rekomendasi",
    },
    {
        "judul": "Tips Efektif Membaca Cepat",
        "ringkasan": "Pelajari teknik speed reading sederhana agar kamu bisa menyelesaikan "
                     "lebih banyak buku tanpa kehilangan pemahaman isi bacaan.",
        "kategori": "Tips & Trik",
    },
    {
        "judul": "Jadwal Kunjungan & Jam Operasional",
        "ringkasan": "Perpustakaan buka setiap hari Senin-Sabtu pukul 08.00-16.00. "
                     "Cek jadwal lengkap dan agenda kegiatan bulanan di sini.",
        "kategori": "Pengumuman",
    },
    {
        "judul": "Cara Meminjam Buku Secara Online",
        "ringkasan": "Setelah login, anggota dapat memesan buku secara online dan "
                     "mengambilnya langsung di meja sirkulasi perpustakaan.",
        "kategori": "Panduan",
    },
]


DEFAULT_BOOKS = [
    {"id": 1, "judul": "Laskar Pelangi", "penulis": "Andrea Hirata", "tahun": "2005", "stok": 5},
    {"id": 2, "judul": "Bumi", "penulis": "Tere Liye", "tahun": "2014", "stok": 3},
    {"id": 3, "judul": "Atomic Habits", "penulis": "James Clear", "tahun": "2018", "stok": 4},
]


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def load_users() -> dict:
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_users(users: dict) -> None:
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)


def register_user(
    nama: str,
    username: str,
    email: str,
    password: str
) -> tuple[bool, str]:

    users = load_users()

    if username in users:
        return False, "Username sudah terdaftar. Silakan gunakan username lain."

    for data in users.values():
        if data.get("email", "").lower() == email.lower():
            return False, "Email sudah terdaftar. Silakan gunakan email lain."

    if len(password) < 8:
        return False, "Password minimal 8 karakter."

    users[username] = {
        "nama": nama,
        "email": email,
        "peran": "Anggota",
        "status": "Aktif",
        "password": hash_password(password)
    }

    save_users(users)

    return True, "Pendaftaran berhasil! Silakan login."


def verify_login(username: str, password: str) -> tuple[bool, str]:

    users = load_users()

    if username not in users:
        return False, "Username tidak ditemukan."

    if users[username].get("status", "Aktif") != "Aktif":
        return False, "Akun Anda tidak aktif."

    if users[username]["password"] != hash_password(password):
        return False, "Password salah."

    return True, "Login berhasil!"


def delete_user(username: str) -> tuple[bool, str]:
    users = load_users()
    if username not in users:
        return False, "User tidak ditemukan."
    del users[username]
    save_users(users)
    return True, "User berhasil dihapus."


def update_user(
    old_username: str,
    new_username: str,
    nama: str,
    email: str,
    role: str,
    status: str,
    new_password: str = ""
):
    users = load_users()
    if old_username not in users:
        return False, "User tidak ditemukan."
    if new_username != old_username and new_username in users:
        return False, "Username baru sudah dipakai user lain."
    for uname, data in users.items():
        if uname != old_username and data.get("email", "").lower() == email.lower():
            return False, "Email sudah dipakai user lain."
    record = users.pop(old_username)
    record["nama"] = nama
    record["email"] = email
    record["role"] = role
    record["status"] = status
    if new_password:
        if len(new_password) < 8:
            return False, "Password minimal 8 karakter."

        record["password"] = hash_password(new_password)
    users[new_username] = record
    save_users(users)
    return True, "User berhasil diperbarui."


def load_books() -> list:
    if not os.path.exists(BOOKS_FILE):
        save_books(DEFAULT_BOOKS)
        return list(DEFAULT_BOOKS)
    try:
        with open(BOOKS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except (json.JSONDecodeError, OSError):
        return []


def save_books(books: list) -> None:
    with open(BOOKS_FILE, "w", encoding="utf-8") as f:
        json.dump(books, f, indent=2, ensure_ascii=False)


def get_next_book_id(books: list) -> int:
    if not books:
        return 1
    return max(int(b.get("id", 0)) for b in books) + 1


def add_book(judul: str, penulis: str, kategori: str, stok: int, tahun: str = "2024") -> tuple[bool, str]:
    books = load_books()
    new_id = get_next_book_id(books)
    books.append({
        "id": new_id, 
        "judul": judul, 
        "penulis": penulis, 
        "kategori": kategori,
        "tahun": tahun, 
        "stok": int(stok)
    })
    save_books(books)
    return True, "Buku berhasil ditambahkan."


def update_book(book_id: int, judul: str, penulis: str, kategori: str, stok: int, tahun: str = "2024") -> tuple[bool, str]:
    books = load_books()
    for b in books:
        if int(b.get("id", 0)) == int(book_id):
            b["judul"] = judul
            b["penulis"] = penulis
            b["kategori"] = kategori
            b["tahun"] = tahun
            b["stok"] = int(stok)
            save_books(books)
            return True, "Buku berhasil diperbarui."
    return False, "Buku tidak ditemukan."


def delete_book(book_id: int) -> tuple[bool, str]:
    books = load_books()
    borrowings = load_borrowings()
    for p in borrowings:
        if int(p.get("book_id", 0)) == int(book_id) and p.get("status") == "Dipinjam":
            return False, "Buku tidak bisa dihapus karena sedang dipinjam."
    filtered = [b for b in books if int(b.get("id", 0)) != int(book_id)]
    if len(filtered) == len(books):
        return False, "Buku tidak ditemukan."
    save_books(filtered)
    return True, "Buku berhasil dihapus."


def find_book(book_id: int):
    for b in load_books():
        if int(b.get("id", 0)) == int(book_id):
            return b
    return None


def adjust_book_stock(book_id: int, delta: int) -> bool:
    books = load_books()
    updated = False
    for b in books:
        if int(b.get("id", 0)) == int(book_id):
            current_stok = int(b.get("stok", 0))
            new_stok = current_stok + delta
            if new_stok < 0:
                return False
            b["stok"] = new_stok
            updated = True
            break
    if updated:
        save_books(books)
        return True
    return False


def load_borrowings() -> list:
    if not os.path.exists(BORROWINGS_FILE):
        return []
    try:
        with open(BORROWINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except (json.JSONDecodeError, OSError):
        return []


def save_borrowings(borrowings: list) -> None:
    with open(BORROWINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(borrowings, f, indent=2, ensure_ascii=False)


def get_next_borrowing_id(borrowings: list) -> int:
    if not borrowings:
        return 1
    return max(int(p.get("id", 0)) for p in borrowings) + 1


def add_borrowing(username: str, book_id: int, tanggal_pinjam: str, tanggal_kembali: str) -> tuple[bool, str]:
    users = load_users()
    if username not in users:
        return False, "Username tidak terdaftar."
    
    try:
        book_id_int = int(book_id)
    except (ValueError, TypeError):
        return False, "ID Buku tidak valid."

    book = find_book(book_id_int)
    if book is None:
        return False, "Buku tidak ditemukan."
    
    if int(book.get("stok", 0)) <= 0:
        return False, "Stok buku habis."

    borrowings = load_borrowings()
    new_id = get_next_borrowing_id(borrowings)
    
    borrowings.append({
        "id": new_id,
        "username": username,
        "book_id": book_id_int,
        "judul": book.get("judul", ""),
        "tanggal_pinjam": tanggal_pinjam,
        "tanggal_kembali": tanggal_kembali,
        "status": "Dipinjam",
    })
    
    save_borrowings(borrowings)
    
    success = adjust_book_stock(book_id_int, -1)
    if not success:
        return False, "Gagal memperbarui stok buku."

    return True, "Peminjaman berhasil ditambahkan dan stok diperbarui."


def update_borrowing(borrow_id: int, username: str, book_id: int, tanggal_pinjam: str, tanggal_kembali: str, status: str) -> tuple[bool, str]:
    borrowings = load_borrowings()
    target = None
    for p in borrowings:
        if int(p.get("id", 0)) == int(borrow_id):
            target = p
            break
    if target is None:
        return False, "Data peminjaman tidak ditemukan."
    
    old_status = target.get("status")
    old_book_id = int(target.get("book_id", 0))
    
    try:
        new_book_id = int(book_id)
    except (ValueError, TypeError):
        return False, "ID Buku tidak valid."

    # DIPERBAIKI: Mengubah "Kembali" menjadi "Dikembalikan" agar sinkron dengan UI
    if old_status == "Dipinjam" and status == "Dikembalikan" and old_book_id == new_book_id:
        adjust_book_stock(old_book_id, 1)
    elif old_status == "Dikembalikan" and status == "Dipinjam":
        book = find_book(new_book_id)
        if book is None:
            return False, "Buku tidak ditemukan."
        if int(book.get("stok", 0)) <= 0:
            return False, "Stok buku habis."
        adjust_book_stock(new_book_id, -1)
    elif old_book_id != new_book_id and old_status == "Dipinjam" and status == "Dipinjam":
        book = find_book(new_book_id)
        if book is None:
            return False, "Buku tidak ditemukan."
        if int(book.get("stok", 0)) <= 0:
            return False, "Stok buku habis."
        adjust_book_stock(old_book_id, 1)
        adjust_book_stock(new_book_id, -1)
        
    target["username"] = username
    target["book_id"] = new_book_id
    book_now = find_book(new_book_id)
    if book_now is not None:
        target["judul"] = book_now.get("judul", target.get("judul", ""))
    target["tanggal_pinjam"] = tanggal_pinjam
    target["tanggal_kembali"] = tanggal_kembali
    target["status"] = status
    save_borrowings(borrowings)
    return True, "Data peminjaman berhasil diperbarui."


def delete_borrowing(borrow_id: int) -> tuple[bool, str]:
    borrowings = load_borrowings()
    target = None
    for p in borrowings:
        if int(p.get("id", 0)) == int(borrow_id):
            target = p
            break
    if target is None:
        return False, "Data peminjaman tidak ditemukan."
    if target.get("status") == "Dipinjam":
        adjust_book_stock(int(target.get("book_id", 0)), 1)
    filtered = [p for p in borrowings if int(p.get("id", 0)) != int(borrow_id)]
    save_borrowings(filtered)
    return True, "Data peminjaman berhasil dihapus."


class HoverButton(tk.Button):
    def __init__(self, master, bg_normal, bg_hover, **kwargs):
        super().__init__(master, bg=bg_normal, activebackground=bg_hover, **kwargs)
        self.bg_normal = bg_normal
        self.bg_hover = bg_hover
        self.bind("<Enter>", lambda e: self.config(bg=self.bg_hover))
        self.bind("<Leave>", lambda e: self.config(bg=self.bg_normal))