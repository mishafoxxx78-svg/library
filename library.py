import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime, timedelta
import os
from typing import List, Optional

# ══════════════════════════════════════════════════════════════
# ПАЛИТРА — Luxury Dark Editorial
# ══════════════════════════════════════════════════════════════
P = {
    "bg":          "#0f0e0b",   # почти-чёрный с тёплым оттенком
    "bg2":         "#161410",   # карточный фон
    "bg3":         "#1d1a14",   # поднятый элемент
    "border":      "#2e2a20",   # граница
    "border_hi":   "#8b6914",   # золотая граница
    "gold":        "#c9a84c",   # основное золото
    "gold_hi":     "#e8c96a",   # светлое золото
    "gold_dim":    "#5c4a1e",   # тусклое золото
    "cream":       "#e8e0c8",   # кремовый текст
    "cream_dim":   "#7a7060",   # тусклый текст
    "cream_lo":    "#3d3828",   # очень тусклый
    "green":       "#4a7c59",   # статус: доступна
    "green_hi":    "#6aaf7e",
    "red":         "#8b3a3a",   # статус: выдана
    "red_hi":      "#c95555",
    "blue":        "#3a5f8b",
    "blue_hi":     "#5a8fbf",
    "sel":         "#2a2416",   # выделенная строка
}

FONT_TITLE  = ("Georgia", 22, "bold")
FONT_HEAD   = ("Georgia", 14, "bold")
FONT_SUB    = ("Georgia", 11, "italic")
FONT_BODY   = ("Georgia", 10)
FONT_SMALL  = ("Georgia", 9)
FONT_MONO   = ("Courier", 10)
FONT_BTN    = ("Georgia", 10, "bold")
FONT_BTN_SM = ("Georgia", 9)


# ══════════════════════════════════════════════════════════════
# ВИДЖЕТЫ
# ══════════════════════════════════════════════════════════════

class GoldButton(tk.Canvas):
    """Кнопка с золотой рамкой и hover-эффектом."""
    def __init__(self, parent, text, command, style="primary",
                 width=160, height=34, font=FONT_BTN, **kw):
        super().__init__(parent, width=width, height=height,
                         bg=P["bg2"], highlightthickness=0, **kw)
        self.cmd = command
        self.text = text
        self.style = style
        self.w, self.h = width, height
        self.font = font
        self._hovered = False
        self._draw()
        self.bind("<Enter>",    self._on_enter)
        self.bind("<Leave>",    self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def _draw(self):
        self.delete("all")
        h = self._hovered

        if self.style == "primary":
            bg_fill = P["gold_dim"] if h else P["bg3"]
            border  = P["gold_hi"] if h else P["gold"]
            fg      = P["bg"] if h else P["gold"]
        elif self.style == "danger":
            bg_fill = "#4a1a1a" if h else P["bg3"]
            border  = P["red_hi"] if h else P["red"]
            fg      = P["cream"] if h else P["red_hi"]
        elif self.style == "ghost":
            bg_fill = P["bg3"] if h else P["bg2"]
            border  = P["border_hi"] if h else P["border"]
            fg      = P["cream"] if h else P["cream_dim"]
        else:
            bg_fill = P["bg3"]
            border  = P["gold_dim"]
            fg      = P["cream_dim"]

        # Фон
        self.create_rectangle(1, 1, self.w - 1, self.h - 1,
                              fill=bg_fill, outline=border, width=1)
        # Угловые засечки
        s = 5
        for x1, y1, x2, y2 in [(1,1,1+s,1),(1,1,1,1+s),
                                 (self.w-1,1,self.w-1-s,1),(self.w-1,1,self.w-1,1+s),
                                 (1,self.h-1,1+s,self.h-1),(1,self.h-1,1,self.h-1-s),
                                 (self.w-1,self.h-1,self.w-1-s,self.h-1),
                                 (self.w-1,self.h-1,self.w-1,self.h-1-s)]:
            self.create_line(x1,y1,x2,y2, fill=border, width=1)

        self.create_text(self.w//2, self.h//2, text=self.text,
                         font=self.font, fill=fg)

    def _on_enter(self, e):
        self._hovered = True;  self._draw()
    def _on_leave(self, e):
        self._hovered = False; self._draw()
    def _on_click(self, e):
        self.cmd()


class GoldEntry(tk.Frame):
    """Поле ввода в стиле тёмной библиотеки."""
    def __init__(self, parent, width=280, placeholder="", show="", **kw):
        super().__init__(parent, bg=P["bg2"], **kw)
        self.placeholder = placeholder
        self._ph_active = False

        self._top = tk.Frame(self, bg=P["gold_dim"], height=1)
        self._top.pack(fill="x")
        self._bot = tk.Frame(self, bg=P["gold_dim"], height=1)

        inner = tk.Frame(self, bg=P["bg3"])
        inner.pack(fill="x")

        self.var = tk.StringVar()
        self._entry = tk.Entry(inner, textvariable=self.var,
                               font=FONT_BODY, width=width // 7,
                               bg=P["bg3"], fg=P["cream"],
                               insertbackground=P["gold"],
                               relief="flat", bd=4,
                               show=show)
        self._entry.pack(fill="x")
        self._bot.pack(fill="x")

        if placeholder:
            self._set_placeholder()
            self._entry.bind("<FocusIn>",  self._clear_ph)
            self._entry.bind("<FocusOut>", self._set_ph_if_empty)
            self._entry.bind("<Enter>",    lambda e: self._top.config(bg=P["gold"]))
            self._entry.bind("<Leave>",    lambda e: self._top.config(bg=P["gold_dim"]))

    def _set_placeholder(self):
        self._ph_active = True
        self._entry.delete(0, "end")
        self._entry.insert(0, self.placeholder)
        self._entry.config(fg=P["cream_dim"])

    def _clear_ph(self, e):
        if self._ph_active:
            self._entry.delete(0, "end")
            self._entry.config(fg=P["cream"])
            self._ph_active = False
        self._top.config(bg=P["gold_hi"])
        self._bot.config(bg=P["gold"])

    def _set_ph_if_empty(self, e):
        self._top.config(bg=P["gold_dim"])
        self._bot.config(bg=P["gold_dim"])
        if not self._entry.get():
            self._set_placeholder()

    def get(self):
        if self._ph_active:
            return ""
        return self.var.get()

    def set(self, val):
        self._ph_active = False
        self._entry.delete(0, "end")
        self._entry.insert(0, val)
        self._entry.config(fg=P["cream"])

    def delete(self, a, b):
        self._entry.delete(a, b)

    def bind_return(self, func):
        self._entry.bind("<Return>", func)

    def focus(self):
        self._entry.focus_set()


class GoldLabel(tk.Label):
    def __init__(self, parent, text, style="body", **kw):
        styles = {
            "title":  {"font": FONT_TITLE, "fg": P["gold"]},
            "head":   {"font": FONT_HEAD,  "fg": P["cream"]},
            "sub":    {"font": FONT_SUB,   "fg": P["cream_dim"]},
            "body":   {"font": FONT_BODY,  "fg": P["cream"]},
            "small":  {"font": FONT_SMALL, "fg": P["cream_dim"]},
            "gold":   {"font": FONT_HEAD,  "fg": P["gold"]},
            "gold_sm":{"font": FONT_SMALL, "fg": P["gold_dim"]},
        }
        cfg = styles.get(style, styles["body"])
        cfg.update(kw)
        super().__init__(parent, text=text, bg=P["bg2"], **cfg)


class Divider(tk.Frame):
    def __init__(self, parent, color=None, **kw):
        super().__init__(parent, bg=color or P["border"], height=1, **kw)


class GoldTreeview(ttk.Treeview):
    """Treeview со стилизацией под тёмную тему."""
    def __init__(self, parent, columns, col_conf, **kw):
        super().__init__(parent, columns=columns, show="headings", **kw)
        for col, (heading, width, anchor) in col_conf.items():
            self.heading(col, text=heading)
            self.column(col, width=width, anchor=anchor, minwidth=30)
        self.tag_configure("available",  foreground=P["green_hi"])
        self.tag_configure("unavailable",foreground=P["red_hi"])
        self.tag_configure("returned",   foreground=P["green_hi"])
        self.tag_configure("active",     foreground=P["blue_hi"])
        self.tag_configure("overdue",    foreground=P["red_hi"])
        self.tag_configure("odd",        background=P["bg3"])
        self.tag_configure("even",       background=P["bg2"])


def apply_theme():
    """Настраивает ttk стиль под тёмную тему."""
    style = ttk.Style()
    style.theme_use("default")

    style.configure(".", background=P["bg2"], foreground=P["cream"],
                    fieldbackground=P["bg3"], font=FONT_BODY,
                    borderwidth=0, relief="flat")
    style.configure("TFrame",      background=P["bg2"])
    style.configure("TLabel",      background=P["bg2"], foreground=P["cream"])
    style.configure("TLabelframe", background=P["bg2"], foreground=P["gold"],
                    bordercolor=P["border"])
    style.configure("TLabelframe.Label", background=P["bg2"],
                    foreground=P["gold"], font=FONT_SUB)
    style.configure("TScrollbar", background=P["bg3"], troughcolor=P["bg"],
                    borderwidth=0, arrowcolor=P["gold_dim"])
    style.map("TScrollbar", background=[("active", P["gold_dim"])])

    # Notebook
    style.configure("TNotebook", background=P["bg"], borderwidth=0,
                    tabmargins=[0, 0, 0, 0])
    style.configure("TNotebook.Tab",
                    background=P["bg"], foreground=P["cream_dim"],
                    font=FONT_BTN_SM, padding=[16, 8],
                    borderwidth=0)
    style.map("TNotebook.Tab",
              background=[("selected", P["bg2"]), ("active", P["bg3"])],
              foreground=[("selected", P["gold"]), ("active", P["cream"])],
              bordercolor=[("selected", P["gold"])])

    # Treeview
    style.configure("Treeview",
                    background=P["bg2"], foreground=P["cream"],
                    fieldbackground=P["bg2"], rowheight=26,
                    font=FONT_BODY, borderwidth=0)
    style.configure("Treeview.Heading",
                    background=P["bg3"], foreground=P["gold"],
                    font=FONT_BTN_SM, relief="flat",
                    borderwidth=0)
    style.map("Treeview",
              background=[("selected", P["sel"])],
              foreground=[("selected", P["gold_hi"])])
    style.map("Treeview.Heading",
              background=[("active", P["gold_dim"])])

    # Combobox
    style.configure("TCombobox",
                    background=P["bg3"], foreground=P["cream"],
                    fieldbackground=P["bg3"],
                    selectbackground=P["sel"],
                    selectforeground=P["gold"])
    style.map("TCombobox",
              fieldbackground=[("readonly", P["bg3"])],
              background=[("readonly", P["bg3"])])


# ══════════════════════════════════════════════════════════════
# МОДЕЛИ (не изменены)
# ══════════════════════════════════════════════════════════════
DATA_DIR = "library_data"
BOOKS_FILE = os.path.join(DATA_DIR, "books.json")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
BORROWINGS_FILE = os.path.join(DATA_DIR, "borrowings.json")


def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


class Book:
    def __init__(self, book_id, title, author, genre, available=True):
        self.id = book_id; self.title = title; self.author = author
        self.genre = genre; self.available = available

    def to_dict(self):
        return {"id": self.id, "title": self.title, "author": self.author,
                "genre": self.genre, "available": self.available}

    @staticmethod
    def from_dict(d):
        return Book(d["id"], d["title"], d["author"], d["genre"], d.get("available", True))


class User:
    def __init__(self, user_id, username, password, role="user"):
        self.id = user_id; self.username = username
        self.password = password; self.role = role

    def to_dict(self):
        return {"id": self.id, "username": self.username,
                "password": self.password, "role": self.role}

    @staticmethod
    def from_dict(d):
        return User(d["id"], d["username"], d["password"], d.get("role", "user"))


class Borrowing:
    def __init__(self, borrow_id, book_id, user_id, borrow_date, due_date, returned=False):
        self.id = borrow_id; self.book_id = book_id; self.user_id = user_id
        self.borrow_date = borrow_date; self.due_date = due_date; self.returned = returned

    def to_dict(self):
        return {"id": self.id, "book_id": self.book_id, "user_id": self.user_id,
                "borrow_date": self.borrow_date, "due_date": self.due_date,
                "returned": self.returned}

    @staticmethod
    def from_dict(d):
        return Borrowing(d["id"], d["book_id"], d["user_id"],
                         d["borrow_date"], d["due_date"], d.get("returned", False))


class LibraryDB:
    def __init__(self):
        ensure_data_dir()
        self.books: List[Book] = []; self.users: List[User] = []
        self.borrowings: List[Borrowing] = []
        self.next_book_id = 1; self.next_user_id = 1; self.next_borrow_id = 1
        self.load_all()

    def load_all(self):
        self.load_books(); self.load_users(); self.load_borrowings()
        if not self.users:   self.create_default_admin()
        if not self.books:   self.add_default_books()

    def save_all(self):
        self.save_books(); self.save_users(); self.save_borrowings()

    def create_default_admin(self):
        self.users.append(User(self.next_user_id, "admin", "admin123", "admin"))
        self.next_user_id += 1; self.save_users()

    def add_default_books(self):
        defaults = [
            ("Война и мир", "Лев Толстой", "Роман"),
            ("Преступление и наказание", "Федор Достоевский", "Роман"),
            ("Мастер и Маргарита", "Михаил Булгаков", "Роман"),
            ("1984", "Джордж Оруэлл", "Антиутопия"),
            ("Гарри Поттер и философский камень", "Джоан Роулинг", "Фэнтези"),
            ("Евгений Онегин", "Александр Пушкин", "Поэзия"),
            ("Собачье сердце", "Михаил Булгаков", "Сатира"),
            ("Анна Каренина", "Лев Толстой", "Роман"),
            ("Три товарища", "Эрих Мария Ремарк", "Роман"),
            ("Маленький принц", "Антуан де Сент-Экзюпери", "Сказка"),
            ("Шерлок Холмс", "Артур Конан Дойл", "Детектив"),
            ("Убить пересмешника", "Харпер Ли", "Роман"),
            ("Великий Гэтсби", "Фрэнсис Фицджеральд", "Роман"),
            ("Дюна", "Фрэнк Герберт", "Фантастика"),
            ("Игра престолов", "Джордж Мартин", "Фэнтези"),
            ("Алхимик", "Пауло Коэльо", "Роман"),
            ("Цветы для Элджернона", "Дэниел Киз", "Фантастика"),
            ("Над пропастью во ржи", "Джером Сэлинджер", "Роман"),
            ("О дивный новый мир", "Олдос Хаксли", "Антиутопия"),
            ("Мартин Иден", "Джек Лондон", "Роман"),
        ]
        for title, author, genre in defaults:
            self.books.append(Book(self.next_book_id, title, author, genre))
            self.next_book_id += 1
        self.save_books()

    def _load_json(self, path):
        if not os.path.exists(path): return {}
        try:
            with open(path, "r", encoding="utf-8") as f: return json.load(f)
        except Exception: return {}

    def _save_json(self, path, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_books(self):
        d = self._load_json(BOOKS_FILE)
        self.books = [Book.from_dict(b) for b in d.get("books", [])]
        self.next_book_id = d.get("next_id", 1)

    def save_books(self):
        self._save_json(BOOKS_FILE, {"books": [b.to_dict() for b in self.books],
                                     "next_id": self.next_book_id})

    def load_users(self):
        d = self._load_json(USERS_FILE)
        self.users = [User.from_dict(u) for u in d.get("users", [])]
        self.next_user_id = d.get("next_id", 1)

    def save_users(self):
        self._save_json(USERS_FILE, {"users": [u.to_dict() for u in self.users],
                                     "next_id": self.next_user_id})

    def load_borrowings(self):
        d = self._load_json(BORROWINGS_FILE)
        self.borrowings = [Borrowing.from_dict(b) for b in d.get("borrowings", [])]
        self.next_borrow_id = d.get("next_id", 1)

    def save_borrowings(self):
        self._save_json(BORROWINGS_FILE,
                        {"borrowings": [b.to_dict() for b in self.borrowings],
                         "next_id": self.next_borrow_id})

    def add_book(self, title, author, genre):
        b = Book(self.next_book_id, title, author, genre)
        self.books.append(b); self.next_book_id += 1; self.save_books(); return b

    def edit_book(self, book_id, title=None, author=None, genre=None):
        for b in self.books:
            if b.id == book_id:
                if title  is not None: b.title  = title
                if author is not None: b.author = author
                if genre  is not None: b.genre  = genre
                self.save_books(); return True
        return False

    def delete_book(self, book_id):
        for i, b in enumerate(self.books):
            if b.id == book_id:
                if any(bor.book_id == book_id and not bor.returned for bor in self.borrowings):
                    return False
                del self.books[i]; self.save_books(); return True
        return False

    def search_books(self, query="", field="all"):
        q = query.lower()
        def match(b):
            if field == "all":
                return q in b.title.lower() or q in b.author.lower() or q in b.genre.lower()
            return q in getattr(b, {"title":"title","author":"author","genre":"genre"}.get(field,"title")).lower()
        return [b for b in self.books if match(b)]

    def register_user(self, username, password, role="user"):
        if any(u.username == username for u in self.users): return None
        u = User(self.next_user_id, username, password, role)
        self.users.append(u); self.next_user_id += 1; self.save_users(); return u

    def login(self, username, password):
        return next((u for u in self.users if u.username == username and u.password == password), None)

    def borrow_book(self, book_id, user_id):
        book = next((b for b in self.books if b.id == book_id), None)
        if not book or not book.available: return False
        now = datetime.now()
        bor = Borrowing(self.next_borrow_id, book_id, user_id,
                        now.strftime("%Y-%m-%d"),
                        (now + timedelta(days=14)).strftime("%Y-%m-%d"))
        self.borrowings.append(bor); self.next_borrow_id += 1
        book.available = False; self.save_all(); return True

    def return_book(self, borrow_id):
        for bor in self.borrowings:
            if bor.id == borrow_id and not bor.returned:
                bor.returned = True
                book = next((b for b in self.books if b.id == bor.book_id), None)
                if book: book.available = True
                self.save_all(); return True
        return False

    def get_user_borrowings(self, user_id):
        return [b for b in self.borrowings if b.user_id == user_id and not b.returned]

    def get_all_borrowings(self):
        return self.borrowings


# ══════════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ UI-функции
# ══════════════════════════════════════════════════════════════

def make_scrolled_tree(parent, tree: GoldTreeview):
    """Обёртка: tree + scrollbar в одном фрейме."""
    frame = tk.Frame(parent, bg=P["bg2"])
    sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")
    return frame


def section_header(parent, title, subtitle=None):
    """Заголовочный блок с золотой линией."""
    f = tk.Frame(parent, bg=P["bg2"])
    tk.Label(f, text=title, font=FONT_HEAD, fg=P["gold"], bg=P["bg2"]).pack(anchor="w")
    if subtitle:
        tk.Label(f, text=subtitle, font=FONT_SMALL, fg=P["cream_dim"], bg=P["bg2"]).pack(anchor="w")
    Divider(f, color=P["gold_dim"]).pack(fill="x", pady=(6, 0))
    return f


def popup_window(root, title, width=420, height=360):
    """Стилизованное всплывающее окно."""
    win = tk.Toplevel(root)
    win.title(title)
    win.geometry(f"{width}x{height}")
    win.resizable(False, False)
    win.configure(bg=P["bg2"])
    win.grab_set()

    # Декоративная верхняя полоска
    tk.Frame(win, bg=P["gold"], height=2).pack(fill="x")
    tk.Label(win, text=title, font=FONT_HEAD, fg=P["gold"],
             bg=P["bg2"], pady=12).pack(fill="x")
    Divider(win).pack(fill="x")

    body = tk.Frame(win, bg=P["bg2"], padx=24, pady=16)
    body.pack(fill="both", expand=True)
    return win, body


def ask_yes_no(root, title, message):
    """Кастомный диалог подтверждения."""
    result = [False]

    win = tk.Toplevel(root)
    win.title(title)
    win.geometry("380x180")
    win.resizable(False, False)
    win.configure(bg=P["bg2"])
    win.grab_set()

    tk.Frame(win, bg=P["gold"], height=2).pack(fill="x")
    tk.Label(win, text=title, font=FONT_HEAD, fg=P["gold"],
             bg=P["bg2"], pady=10).pack(fill="x")
    Divider(win).pack(fill="x")

    tk.Label(win, text=message, font=FONT_BODY, fg=P["cream"],
             bg=P["bg2"], wraplength=320, pady=14).pack()

    bf = tk.Frame(win, bg=P["bg2"])
    bf.pack(pady=8)

    def yes():
        result[0] = True; win.destroy()

    GoldButton(bf, "Да, подтвердить", yes, style="primary",
               width=160, height=32).pack(side="left", padx=6)
    GoldButton(bf, "Отмена", win.destroy, style="ghost",
               width=110, height=32).pack(side="left", padx=6)

    win.wait_window()
    return result[0]


def show_info(root, title, message):
    win, body = popup_window(root, title, 380, 160)
    tk.Label(body, text=message, font=FONT_BODY, fg=P["cream"],
             bg=P["bg2"], wraplength=320, justify="center").pack(pady=8)
    GoldButton(body, "ОК", win.destroy, style="ghost", width=100, height=30).pack(pady=4)
    win.wait_window()


def show_error(root, title, message):
    win, body = popup_window(root, title, 380, 160)
    tk.Label(body, text=message, font=FONT_BODY, fg=P["red_hi"],
             bg=P["bg2"], wraplength=320, justify="center").pack(pady=8)
    GoldButton(body, "ОК", win.destroy, style="danger", width=100, height=30).pack(pady=4)
    win.wait_window()


# ══════════════════════════════════════════════════════════════
# ПРИЛОЖЕНИЕ
# ══════════════════════════════════════════════════════════════

class LibraryApp:
    def __init__(self):
        self.db = LibraryDB()
        self.current_user: Optional[User] = None

        self.root = tk.Tk()
        self.root.title("Книжный Мир")
        self.root.geometry("1060x720")
        self.root.minsize(900, 650)
        self.root.configure(bg=P["bg"])

        # status_var должна существовать до любых вкладок
        self.status_var = tk.StringVar(value="")

        apply_theme()
        self.create_login_window()

    # ──────────────────────────────────────────────────────────
    # ОКНО ВХОДА
    # ──────────────────────────────────────────────────────────
    def create_login_window(self):
        for w in self.root.winfo_children(): w.destroy()
        self.root.title("Книжный Мир — Вход")

        # Декоративная полоска
        tk.Frame(self.root, bg=P["gold"], height=3).pack(fill="x")

        outer = tk.Frame(self.root, bg=P["bg"])
        outer.pack(fill="both", expand=True)

        # Центральная карточка
        card = tk.Frame(outer, bg=P["bg2"], bd=0)
        card.place(relx=0.5, rely=0.5, anchor="center", width=420, height=520)

        # Боковая золотая полоска карточки
        tk.Frame(card, bg=P["gold"], width=3).pack(side="left", fill="y")

        content = tk.Frame(card, bg=P["bg2"], padx=36, pady=32)
        content.pack(fill="both", expand=True)

        # Логотип
        tk.Label(content, text="◈", font=("Georgia", 28), fg=P["gold"],
                 bg=P["bg2"]).pack()
        tk.Label(content, text="Книжный Мир", font=FONT_TITLE,
                 fg=P["gold"], bg=P["bg2"]).pack()
        tk.Label(content, text="Система управления библиотекой",
                 font=FONT_SUB, fg=P["cream_dim"], bg=P["bg2"]).pack(pady=(2, 0))

        Divider(content, color=P["gold_dim"]).pack(fill="x", pady=20)

        # Поля
        tk.Label(content, text="Имя пользователя", font=FONT_SMALL,
                 fg=P["cream_dim"], bg=P["bg2"]).pack(anchor="w")
        self.login_username = GoldEntry(content, width=320, placeholder="Введите логин")
        self.login_username.pack(fill="x", pady=(4, 14))

        tk.Label(content, text="Пароль", font=FONT_SMALL,
                 fg=P["cream_dim"], bg=P["bg2"]).pack(anchor="w")
        self.login_password = GoldEntry(content, width=320,
                                        placeholder="Введите пароль", show="●")
        self.login_password.pack(fill="x", pady=(4, 20))

        # Кнопки
        GoldButton(content, "Войти в систему", self.do_login,
                   style="primary", width=340, height=38,
                   font=FONT_HEAD).pack(fill="x")

        tk.Frame(content, bg=P["bg2"], height=8).pack()
        GoldButton(content, "Создать аккаунт", self.show_register,
                   style="ghost", width=340, height=34).pack(fill="x")

        Divider(content, color=P["border"]).pack(fill="x", pady=16)
        tk.Label(content, text="По умолчанию: admin / admin123",
                 font=FONT_SMALL, fg=P["cream_lo"], bg=P["bg2"]).pack()

        self.login_password.bind_return(lambda e: self.do_login())
        self.login_username.focus()

        # Нижняя полоска
        tk.Frame(self.root, bg=P["border"], height=1).pack(side="bottom", fill="x")
        tk.Label(self.root, text="© Книжный Мир  v2.0",
                 font=FONT_SMALL, fg=P["cream_lo"], bg=P["bg"]).pack(side="bottom", pady=6)

    def do_login(self):
        username = self.login_username.get().strip()
        password = self.login_password.get().strip()
        user = self.db.login(username, password)
        if user:
            self.current_user = user
            self.root.unbind("<Return>")
            self.create_main_window()
        else:
            show_error(self.root, "Ошибка входа", "Неверный логин или пароль.")

    def show_register(self):
        win, body = popup_window(self.root, "Регистрация", 420, 340)

        tk.Label(body, text="Имя пользователя", font=FONT_SMALL,
                 fg=P["cream_dim"], bg=P["bg2"]).pack(anchor="w")
        uname_e = GoldEntry(body, width=340, placeholder="Минимум 3 символа")
        uname_e.pack(fill="x", pady=(4, 14))

        tk.Label(body, text="Пароль", font=FONT_SMALL,
                 fg=P["cream_dim"], bg=P["bg2"]).pack(anchor="w")
        pass_e = GoldEntry(body, width=340, placeholder="Минимум 4 символа", show="●")
        pass_e.pack(fill="x", pady=(4, 20))

        def register():
            u, p = uname_e.get().strip(), pass_e.get().strip()
            if not u or not p:
                show_error(win, "Ошибка", "Заполните все поля")
            elif len(u) < 3:
                show_error(win, "Ошибка", "Логин минимум 3 символа")
            elif len(p) < 4:
                show_error(win, "Ошибка", "Пароль минимум 4 символа")
            elif self.db.register_user(u, p):
                show_info(win, "Готово", f"Аккаунт «{u}» создан.\nТеперь войдите в систему.")
                win.destroy()
            else:
                show_error(win, "Ошибка", "Пользователь уже существует")

        GoldButton(body, "Зарегистрироваться", register,
                   style="primary", width=340, height=38).pack(fill="x")
        pass_e.bind_return(lambda e: register())
        uname_e.focus()

    # ──────────────────────────────────────────────────────────
    # ГЛАВНОЕ ОКНО
    # ──────────────────────────────────────────────────────────
    def create_main_window(self):
        for w in self.root.winfo_children(): w.destroy()
        role_text = "Администратор" if self.current_user.role == "admin" else "Читатель"
        self.root.title(f"Книжный Мир — {self.current_user.username}")

        # ── Верхняя панель (topbar) ─────────────────────────
        tk.Frame(self.root, bg=P["gold"], height=2).pack(fill="x")

        topbar = tk.Frame(self.root, bg=P["bg3"], height=50)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        tk.Label(topbar, text="◈  Книжный Мир", font=FONT_HEAD,
                 fg=P["gold"], bg=P["bg3"]).pack(side="left", padx=20)

        # Статистика
        if self.current_user.role == "admin":
            stats = (f"  Книг: {len(self.db.books)}  ·  "
                     f"Читателей: {len([u for u in self.db.users if u.role=='user'])}  ·  "
                     f"На руках: {len([b for b in self.db.borrowings if not b.returned])}")
            tk.Label(topbar, text=stats, font=FONT_SMALL,
                     fg=P["cream_dim"], bg=P["bg3"]).pack(side="left", padx=10)

        # Пользователь + выход
        right = tk.Frame(topbar, bg=P["bg3"])
        right.pack(side="right", padx=16)
        tk.Label(right, text=f"◐  {self.current_user.username}  ·  {role_text}",
                 font=FONT_SMALL, fg=P["cream_dim"], bg=P["bg3"]).pack(side="left", padx=10)
        GoldButton(right, "Выйти", self.logout, style="ghost",
                   width=80, height=28, font=FONT_BTN_SM).pack(side="left")

        tk.Frame(self.root, bg=P["border"], height=1).pack(fill="x")

        # ── Notebook ────────────────────────────────────────
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=0, pady=0)

        self.all_books_tab = tk.Frame(self.notebook, bg=P["bg2"])
        self.search_tab    = tk.Frame(self.notebook, bg=P["bg2"])
        self.my_books_tab  = tk.Frame(self.notebook, bg=P["bg2"])

        self.notebook.add(self.all_books_tab, text="  📖  Все книги  ")
        self.notebook.add(self.search_tab,    text="  🔍  Поиск  ")
        self.notebook.add(self.my_books_tab,  text="  📋  Мои книги  ")

        if self.current_user.role == "admin":
            self.all_bor_tab = tk.Frame(self.notebook, bg=P["bg2"])
            self.manage_tab  = tk.Frame(self.notebook, bg=P["bg2"])
            self.notebook.add(self.all_bor_tab, text="  📊  Заимствования  ")
            self.notebook.add(self.manage_tab,  text="  ⚙  Управление  ")

        self.build_all_books_tab()
        self.build_search_tab()
        self.build_my_books_tab()
        if self.current_user.role == "admin":
            self.build_all_borrowings_tab()
            self.build_manage_tab()

        # Нижняя строка статуса
        tk.Frame(self.root, bg=P["border"], height=1).pack(fill="x")
        self.status_var.set("Готов к работе")
        tk.Label(self.root, textvariable=self.status_var, font=FONT_SMALL,
                 fg=P["cream_lo"], bg=P["bg"], anchor="w").pack(
                     fill="x", padx=16, pady=3)

    def _set_status(self, msg):
        self.status_var.set(msg)

    def logout(self):
        if ask_yes_no(self.root, "Выход", "Выйти из аккаунта?"):
            self.current_user = None
            self.create_login_window()

    def show_about(self):
        show_info(self.root, "О программе",
                  "Книжный Мир\nСистема управления библиотекой\nВерсия 2.0")

    # ──────────────────────────────────────────────────────────
    # ВКЛАДКА: ВСЕ КНИГИ
    # ──────────────────────────────────────────────────────────
    def build_all_books_tab(self):
        for w in self.all_books_tab.winfo_children(): w.destroy()
        tab = self.all_books_tab

        # Toolbar
        bar = tk.Frame(tab, bg=P["bg3"], pady=10, padx=16)
        bar.pack(fill="x")

        tk.Label(bar, text="Поиск:", font=FONT_SMALL,
                 fg=P["cream_dim"], bg=P["bg3"]).pack(side="left")
        self.all_search_var = tk.StringVar()
        se = tk.Entry(bar, textvariable=self.all_search_var,
                      font=FONT_BODY, width=36,
                      bg=P["bg2"], fg=P["cream"], insertbackground=P["gold"],
                      relief="flat", bd=6)
        se.pack(side="left", padx=8)

        GoldButton(bar, "Найти", self.refresh_all_books,
                   style="primary", width=80, height=30, font=FONT_BTN_SM).pack(side="left", padx=4)
        GoldButton(bar, "Сбросить", self.reset_all_books,
                   style="ghost", width=90, height=30, font=FONT_BTN_SM).pack(side="left")

        if self.current_user.role == "user":
            GoldButton(bar, "📥 Взять книгу", self.borrow_selected_book,
                       style="primary", width=130, height=30, font=FONT_BTN_SM
                       ).pack(side="right", padx=8)

        # Счётчик
        self.all_count_var = tk.StringVar()
        tk.Label(bar, textvariable=self.all_count_var, font=FONT_SMALL,
                 fg=P["gold_dim"], bg=P["bg3"]).pack(side="right", padx=12)

        tk.Frame(tab, bg=P["border"], height=1).pack(fill="x")

        # Таблица
        cols = ("ID","Название","Автор","Жанр","Статус")
        col_conf = {
            "ID":       ("ID",       52,  "center"),
            "Название": ("Название", 320, "w"),
            "Автор":    ("Автор",    200, "w"),
            "Жанр":     ("Жанр",     140, "w"),
            "Статус":   ("Статус",   110, "center"),
        }
        self.all_tree = GoldTreeview(tab, cols, col_conf, height=22)
        frame = make_scrolled_tree(tab, self.all_tree)
        frame.pack(fill="both", expand=True, padx=0, pady=0)

        self.refresh_all_books()
        se.bind("<Return>", lambda e: self.refresh_all_books())

    def refresh_all_books(self):
        for i in self.all_tree.get_children(): self.all_tree.delete(i)
        q = self.all_search_var.get().strip().lower()
        books = self.db.search_books(q) if q else self.db.books
        for idx, b in enumerate(books):
            status = "✦ Доступна" if b.available else "✧ Выдана"
            tag    = ("available" if b.available else "unavailable",
                      "odd" if idx % 2 else "even")[1]
            row_tags = ("available",) if b.available else ("unavailable",)
            self.all_tree.insert("", "end",
                                 values=(b.id, b.title, b.author, b.genre, status),
                                 tags=row_tags)
        self.all_count_var.set(f"Показано: {len(books)}")
        self._set_status(f"Книг в списке: {len(books)}")

    def reset_all_books(self):
        self.all_search_var.set("")
        self.refresh_all_books()

    def borrow_selected_book(self):
        sel = self.all_tree.selection()
        if not sel:
            show_error(self.root, "Внимание", "Выберите книгу из списка"); return
        book_id = int(self.all_tree.item(sel[0])["values"][0])
        book = next((b for b in self.db.books if b.id == book_id), None)
        if not book or not book.available:
            show_error(self.root, "Недоступна", "Эта книга уже выдана"); return
        if ask_yes_no(self.root, "Взять книгу",
                      f"Взять «{book.title}»?\nСрок возврата: 14 дней"):
            if self.db.borrow_book(book_id, self.current_user.id):
                show_info(self.root, "Выдана", f"«{book.title}» выдана на 14 дней")
                self.refresh_all_books(); self.refresh_my_books()
                self._set_status(f"Выдана книга: {book.title}")

    # ──────────────────────────────────────────────────────────
    # ВКЛАДКА: ПОИСК
    # ──────────────────────────────────────────────────────────
    def build_search_tab(self):
        for w in self.search_tab.winfo_children(): w.destroy()
        tab = self.search_tab

        panel = tk.Frame(tab, bg=P["bg3"], padx=20, pady=16)
        panel.pack(fill="x")

        section_header(panel, "Расширенный поиск").pack(fill="x", pady=(0, 14))

        row1 = tk.Frame(panel, bg=P["bg3"])
        row1.pack(fill="x")

        tk.Label(row1, text="Поле:", font=FONT_SMALL,
                 fg=P["cream_dim"], bg=P["bg3"]).pack(side="left")
        self.search_field = ttk.Combobox(row1,
                                         values=["Везде","Названию","Автору","Жанру"],
                                         width=14, state="readonly", font=FONT_BODY)
        self.search_field.current(0)
        self.search_field.pack(side="left", padx=10)

        tk.Label(row1, text="Запрос:", font=FONT_SMALL,
                 fg=P["cream_dim"], bg=P["bg3"]).pack(side="left")
        self.search_query_e = tk.Entry(row1, font=FONT_BODY, width=36,
                                       bg=P["bg2"], fg=P["cream"],
                                       insertbackground=P["gold"],
                                       relief="flat", bd=6)
        self.search_query_e.pack(side="left", padx=10)
        GoldButton(row1, "Искать", self.do_search,
                   style="primary", width=90, height=30, font=FONT_BTN_SM).pack(side="left")

        self.search_count_var = tk.StringVar(value="")
        tk.Label(panel, textvariable=self.search_count_var, font=FONT_SMALL,
                 fg=P["gold_dim"], bg=P["bg3"]).pack(anchor="w", pady=(8, 0))

        tk.Frame(tab, bg=P["border"], height=1).pack(fill="x")

        cols = ("ID","Название","Автор","Жанр","Статус")
        col_conf = {
            "ID":       ("ID",       52, "center"),
            "Название": ("Название",320, "w"),
            "Автор":    ("Автор",   200, "w"),
            "Жанр":     ("Жанр",   140, "w"),
            "Статус":   ("Статус", 110, "center"),
        }
        self.search_tree = GoldTreeview(tab, cols, col_conf)
        make_scrolled_tree(tab, self.search_tree).pack(fill="both", expand=True)
        self.search_query_e.bind("<Return>", lambda e: self.do_search())

    def do_search(self):
        q = self.search_query_e.get().strip()
        field_map = {"Везде":"all","Названию":"title","Автору":"author","Жанру":"genre"}
        results = self.db.search_books(q, field_map[self.search_field.get()])
        for i in self.search_tree.get_children(): self.search_tree.delete(i)
        for b in results:
            status = "✦ Доступна" if b.available else "✧ Выдана"
            tags   = ("available",) if b.available else ("unavailable",)
            self.search_tree.insert("", "end",
                                    values=(b.id, b.title, b.author, b.genre, status),
                                    tags=tags)
        self.search_count_var.set(f"Найдено: {len(results)}")
        self._set_status(f"Поиск «{q}»: найдено {len(results)}")

    # ──────────────────────────────────────────────────────────
    # ВКЛАДКА: МОИ КНИГИ
    # ──────────────────────────────────────────────────────────
    def build_my_books_tab(self):
        for w in self.my_books_tab.winfo_children(): w.destroy()
        tab = self.my_books_tab

        bar = tk.Frame(tab, bg=P["bg3"], padx=16, pady=10)
        bar.pack(fill="x")
        section_header(bar, "Мои книги",
                        "Книги, которые сейчас у вас на руках").pack(fill="x", pady=(0,8))
        GoldButton(bar, "📤 Вернуть книгу", self.return_selected_book,
                   style="primary", width=160, height=32, font=FONT_BTN_SM).pack(anchor="w")

        tk.Frame(tab, bg=P["border"], height=1).pack(fill="x")

        cols = ("ID","Книга","Дата выдачи","Срок возврата","Статус")
        col_conf = {
            "ID":           ("ID",           52, "center"),
            "Книга":        ("Книга",        340, "w"),
            "Дата выдачи":  ("Дата выдачи",  130, "center"),
            "Срок возврата":("Срок возврата",130, "center"),
            "Статус":       ("Статус",       130, "center"),
        }
        self.my_tree = GoldTreeview(tab, cols, col_conf)
        make_scrolled_tree(tab, self.my_tree).pack(fill="both", expand=True)

        self.refresh_my_books()

    def refresh_my_books(self):
        for i in self.my_tree.get_children(): self.my_tree.delete(i)
        for bor in self.db.get_user_borrowings(self.current_user.id):
            book = next((b for b in self.db.books if b.id == bor.book_id), None)
            title = book.title if book else "Неизвестно"
            due = datetime.strptime(bor.due_date, "%Y-%m-%d")
            if datetime.now() > due:
                status, tag = "⚠ Просрочена!", "overdue"
            else:
                status, tag = "◌ На руках",    "active"
            self.my_tree.insert("", "end",
                                values=(bor.id, title, bor.borrow_date, bor.due_date, status),
                                tags=(tag,))

    def return_selected_book(self):
        sel = self.my_tree.selection()
        if not sel:
            show_error(self.root, "Внимание", "Выберите книгу для возврата"); return
        borrow_id = int(self.my_tree.item(sel[0])["values"][0])
        book_title = self.my_tree.item(sel[0])["values"][1]
        if ask_yes_no(self.root, "Вернуть книгу", f"Вернуть «{book_title}»?"):
            if self.db.return_book(borrow_id):
                show_info(self.root, "Возвращена", "Книга успешно возвращена")
                self.refresh_my_books(); self.refresh_all_books()
                self._set_status(f"Возвращена книга: {book_title}")
            else:
                show_error(self.root, "Ошибка", "Не удалось вернуть книгу")

    # ──────────────────────────────────────────────────────────
    # ВКЛАДКА: ВСЕ ЗАИМСТВОВАНИЯ (АДМИН)
    # ──────────────────────────────────────────────────────────
    def build_all_borrowings_tab(self):
        for w in self.all_bor_tab.winfo_children(): w.destroy()
        tab = self.all_bor_tab

        bar = tk.Frame(tab, bg=P["bg3"], padx=16, pady=10)
        bar.pack(fill="x")
        section_header(bar, "Все заимствования", "Полный журнал выдачи книг").pack(fill="x", pady=(0,8))
        bf = tk.Frame(bar, bg=P["bg3"])
        bf.pack(anchor="w")
        GoldButton(bf, "🔄 Обновить", self.refresh_all_bor,
                   style="ghost", width=120, height=30, font=FONT_BTN_SM).pack(side="left", padx=(0,8))
        GoldButton(bf, "📤 Отметить возврат", self.admin_return_book,
                   style="primary", width=170, height=30, font=FONT_BTN_SM).pack(side="left")

        tk.Frame(tab, bg=P["border"], height=1).pack(fill="x")

        cols = ("ID","Книга","Пользователь","Дата выдачи","Срок возврата","Статус")
        col_conf = {
            "ID":           ("ID",           50, "center"),
            "Книга":        ("Книга",        260, "w"),
            "Пользователь": ("Пользователь", 140, "w"),
            "Дата выдачи":  ("Дата выдачи",  120, "center"),
            "Срок возврата":("Срок возврата",120, "center"),
            "Статус":       ("Статус",       130, "center"),
        }
        self.bor_tree = GoldTreeview(tab, cols, col_conf)
        make_scrolled_tree(tab, self.bor_tree).pack(fill="both", expand=True)

        self.refresh_all_bor()

    def refresh_all_bor(self):
        for i in self.bor_tree.get_children(): self.bor_tree.delete(i)
        for bor in self.db.get_all_borrowings():
            book = next((b for b in self.db.books  if b.id == bor.book_id), None)
            user = next((u for u in self.db.users  if u.id == bor.user_id), None)
            book_title = book.title    if book else "?"
            username   = user.username if user else "?"
            if bor.returned:
                status, tag = "✦ Возвращена", "returned"
            else:
                due = datetime.strptime(bor.due_date, "%Y-%m-%d")
                if datetime.now() > due:
                    status, tag = "⚠ Просрочена!", "overdue"
                else:
                    status, tag = "◌ На руках",    "active"
            self.bor_tree.insert("", "end",
                                 values=(bor.id, book_title, username,
                                         bor.borrow_date, bor.due_date, status),
                                 tags=(tag,))

    def admin_return_book(self):
        sel = self.bor_tree.selection()
        if not sel:
            show_error(self.root, "Внимание", "Выберите запись"); return
        borrow_id  = int(self.bor_tree.item(sel[0])["values"][0])
        book_title = self.bor_tree.item(sel[0])["values"][1]
        if ask_yes_no(self.root, "Возврат", f"Отметить «{book_title}» как возвращённую?"):
            if self.db.return_book(borrow_id):
                show_info(self.root, "Готово", "Книга отмечена возвращённой")
                self.refresh_all_bor(); self.refresh_all_books()
            else:
                show_error(self.root, "Ошибка", "Не удалось отметить возврат")

    # ──────────────────────────────────────────────────────────
    # ВКЛАДКА: УПРАВЛЕНИЕ КНИГАМИ (АДМИН)
    # ──────────────────────────────────────────────────────────
    def build_manage_tab(self):
        for w in self.manage_tab.winfo_children(): w.destroy()
        tab = self.manage_tab

        # Левая панель — форма добавления
        left = tk.Frame(tab, bg=P["bg3"], width=320)
        left.pack(side="left", fill="y", padx=0)
        left.pack_propagate(False)

        # Декоративная полоска
        tk.Frame(left, bg=P["gold"], width=2).pack(side="right", fill="y")

        form = tk.Frame(left, bg=P["bg3"], padx=20, pady=20)
        form.pack(fill="both", expand=True)

        section_header(form, "Добавить книгу").pack(fill="x", pady=(0, 16))

        lbl_cfg = {"font": FONT_SMALL, "fg": P["cream_dim"], "bg": P["bg3"]}

        tk.Label(form, text="Название", **lbl_cfg).pack(anchor="w")
        self.add_title = GoldEntry(form, width=260, placeholder="Название книги")
        self.add_title.pack(fill="x", pady=(4, 12))

        tk.Label(form, text="Автор", **lbl_cfg).pack(anchor="w")
        self.add_author = GoldEntry(form, width=260, placeholder="Имя автора")
        self.add_author.pack(fill="x", pady=(4, 12))

        tk.Label(form, text="Жанр", **lbl_cfg).pack(anchor="w")
        self.add_genre = GoldEntry(form, width=260, placeholder="Жанр")
        self.add_genre.pack(fill="x", pady=(4, 20))

        GoldButton(form, "✚  Добавить", self.add_new_book,
                   style="primary", width=260, height=36).pack(fill="x")
        tk.Frame(form, bg=P["bg3"], height=6).pack()
        GoldButton(form, "Очистить", self.clear_add_fields,
                   style="ghost", width=260, height=30, font=FONT_BTN_SM).pack(fill="x")

        Divider(form, color=P["border"]).pack(fill="x", pady=18)

        tk.Label(form, text="Подсказки", font=FONT_SMALL,
                 fg=P["gold_dim"], bg=P["bg3"]).pack(anchor="w")
        hints = [
            "✦ Двойной клик — редактировать",
            "✦ Delete — удалить выбранную",
        ]
        for h in hints:
            tk.Label(form, text=h, font=FONT_SMALL,
                     fg=P["cream_lo"], bg=P["bg3"]).pack(anchor="w", pady=1)

        # Правая часть — список книг
        right = tk.Frame(tab, bg=P["bg2"])
        right.pack(side="left", fill="both", expand=True)

        header = tk.Frame(right, bg=P["bg3"], padx=16, pady=10)
        header.pack(fill="x")
        section_header(header, "Каталог книг",
                       "Все книги в системе").pack(fill="x")

        tk.Frame(right, bg=P["border"], height=1).pack(fill="x")

        cols = ("ID","Название","Автор","Жанр","Статус")
        col_conf = {
            "ID":       ("ID",       52, "center"),
            "Название": ("Название",280, "w"),
            "Автор":    ("Автор",   200, "w"),
            "Жанр":     ("Жанр",   140, "w"),
            "Статус":   ("Статус",  80, "center"),
        }
        self.manage_tree = GoldTreeview(right, cols, col_conf, height=22)
        make_scrolled_tree(right, self.manage_tree).pack(fill="both", expand=True)

        self.manage_tree.bind("<Double-1>", self.edit_book_dialog)
        self.manage_tree.bind("<Delete>",   self.delete_selected_book)

        self.refresh_manage_books()

    def clear_add_fields(self):
        self.add_title.delete(0, "end");  self.add_title._set_placeholder()
        self.add_author.delete(0, "end"); self.add_author._set_placeholder()
        self.add_genre.delete(0, "end");  self.add_genre._set_placeholder()
        self.add_title.focus()

    def add_new_book(self):
        t, a, g = self.add_title.get().strip(), self.add_author.get().strip(), self.add_genre.get().strip()
        if not t or not a or not g:
            show_error(self.root, "Ошибка", "Заполните все три поля"); return
        book = self.db.add_book(t, a, g)
        show_info(self.root, "Добавлена", f"Книга «{book.title}» добавлена (ID: {book.id})")
        self.clear_add_fields()
        self.refresh_manage_books(); self.refresh_all_books()
        self._set_status(f"Добавлена книга: {book.title}")

    def refresh_manage_books(self):
        for i in self.manage_tree.get_children(): self.manage_tree.delete(i)
        for b in self.db.books:
            status = "✦" if b.available else "✧"
            tags   = ("available",) if b.available else ("unavailable",)
            self.manage_tree.insert("", "end",
                                    values=(b.id, b.title, b.author, b.genre, status),
                                    tags=tags)

    def edit_book_dialog(self, event):
        sel = self.manage_tree.selection()
        if not sel: return
        vals = self.manage_tree.item(sel[0])["values"]
        book_id = int(vals[0])

        win, body = popup_window(self.root, f"Редактировать книгу #{book_id}", 440, 320)

        lbl_cfg = {"font": FONT_SMALL, "fg": P["cream_dim"], "bg": P["bg2"]}
        tk.Label(body, text="Название", **lbl_cfg).pack(anchor="w")
        te = GoldEntry(body, width=360); te.set(str(vals[1])); te.pack(fill="x", pady=(4,12))

        tk.Label(body, text="Автор", **lbl_cfg).pack(anchor="w")
        ae = GoldEntry(body, width=360); ae.set(str(vals[2])); ae.pack(fill="x", pady=(4,12))

        tk.Label(body, text="Жанр", **lbl_cfg).pack(anchor="w")
        ge = GoldEntry(body, width=360); ge.set(str(vals[3])); ge.pack(fill="x", pady=(4,16))

        def save():
            nt, na, ng = te.get().strip(), ae.get().strip(), ge.get().strip()
            if not nt or not na or not ng:
                show_error(win, "Ошибка", "Все поля должны быть заполнены"); return
            if self.db.edit_book(book_id, nt, na, ng):
                show_info(win, "Сохранено", "Данные книги обновлены")
                win.destroy()
                self.refresh_manage_books(); self.refresh_all_books()
            else:
                show_error(win, "Ошибка", "Не удалось сохранить")

        GoldButton(body, "💾  Сохранить", save,
                   style="primary", width=360, height=36).pack(fill="x")
        te.focus()

    def delete_selected_book(self, event):
        sel = self.manage_tree.selection()
        if not sel: return
        vals = self.manage_tree.item(sel[0])["values"]
        book_id, book_title = int(vals[0]), vals[1]
        if ask_yes_no(self.root, "Удалить книгу",
                      f"Удалить «{book_title}»?\n\nДействие необратимо!"):
            if self.db.delete_book(book_id):
                show_info(self.root, "Удалена", f"«{book_title}» удалена из каталога")
                self.refresh_manage_books(); self.refresh_all_books()
                self._set_status(f"Удалена книга: {book_title}")
            else:
                show_error(self.root, "Нельзя удалить",
                           "Книга сейчас на руках у читателя.")


# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = LibraryApp()
    app.root.mainloop()