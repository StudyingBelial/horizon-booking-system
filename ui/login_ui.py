"""
ui/login_ui.py — Login screen with role-based redirection.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from controllers.auth_controller import AuthController
from utils.constants import Role


# ── Shared colour palette used across all windows ────────────────────────────
PALETTE = {
    "bg":       "#0F0F1A",   # deep navy-black
    "surface":  "#1A1A2E",   # card background
    "accent":   "#00A8FF",   # vibrant electric blue
    "accent2":  "#007BFF",   # deeper blue accent
    "text":     "#E0E0E0",   # primary text
    "muted":    "#7A7A9A",   # secondary text
    "success":  "#2ECC71",
    "warning":  "#F39C12",
    "border":   "#2A2A4A",
}
# ... existing font constants ...
FONT_TITLE  = ("Helvetica", 22, "bold")
FONT_SUB    = ("Helvetica", 11)
FONT_LABEL  = ("Helvetica", 10)
FONT_BUTTON = ("Helvetica", 11, "bold")
FONT_INPUT  = ("Helvetica", 11)


def apply_dark_style(root):
    """Apply ttk dark styling globally."""
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(".",
        background=PALETTE["bg"],
        foreground=PALETTE["text"],
        fieldbackground=PALETTE["surface"],
        insertcolor=PALETTE["text"],
        bordercolor=PALETTE["border"],
        troughcolor=PALETTE["surface"],
        selectbackground=PALETTE["accent2"],
        selectforeground=PALETTE["text"],
        font=FONT_LABEL,
    )
    style.configure("TFrame",  background=PALETTE["bg"])
    style.configure("TLabel",  background=PALETTE["bg"],  foreground=PALETTE["text"])
    style.configure("TEntry",  fieldbackground=PALETTE["surface"],
                    foreground=PALETTE["text"], insertcolor=PALETTE["text"],
                    bordercolor=PALETTE["border"])
    style.configure("Accent.TButton",
        background=PALETTE["accent"], foreground="white",
        font=FONT_BUTTON, padding=(12, 6), relief="flat",
    )
    style.map("Accent.TButton",
        background=[("active", PALETTE["accent2"]), ("pressed", "#0056b3")],
    )
    style.configure("TButton",
        background=PALETTE["accent2"], foreground="white",
        font=FONT_BUTTON, padding=(10, 5), relief="flat",
    )
    style.map("TButton",
        background=[("active", "#0056b3"), ("pressed", "#004085")],
    )
    style.configure("TCombobox",
        fieldbackground=PALETTE["surface"], background=PALETTE["surface"],
        foreground=PALETTE["text"], selectbackground=PALETTE["accent2"],
    )
    style.configure("Treeview",
        background=PALETTE["surface"], foreground=PALETTE["text"],
        rowheight=26, fieldbackground=PALETTE["surface"],
        bordercolor=PALETTE["border"],
    )
    style.configure("Treeview.Heading",
        background=PALETTE["accent2"], foreground="white",
        font=("Helvetica", 10, "bold"),
    )
    style.map("Treeview", background=[("selected", PALETTE["accent"])])
    style.configure("TScrollbar",
        background=PALETTE["surface"], troughcolor=PALETTE["bg"],
        arrowcolor=PALETTE["muted"],
    )
    style.configure("TNotebook",
        background=PALETTE["bg"], tabmargins=[2, 5, 2, 0],
    )
    style.configure("TNotebook.Tab",
        background=PALETTE["accent2"], foreground="white",
        padding=[12, 4], font=("Helvetica", 10),
    )
    style.map("TNotebook.Tab",
        background=[("selected", PALETTE["accent"])],
        foreground=[("selected", "white")],
    )


class LoginUI(tk.Tk):
    """Main application window — shown first as the login gate."""

    def __init__(self):
        super().__init__()
        self.title("Horizon Cinemas — Login")
        self.geometry("460x660")
        self.resizable(False, False)
        self.configure(bg=PALETTE["bg"])
        apply_dark_style(self)
        self._build()

    def _build(self):
        # ── Header ────────────────────────────────────────────────────────────
        header = tk.Frame(self, bg=PALETTE["bg"])
        header.pack(pady=(40, 0))

        tk.Label(header, text="🎬", font=("Helvetica", 42),
                 bg=PALETTE["bg"], fg=PALETTE["accent"]).pack()
        tk.Label(header, text="HORIZON CINEMAS",
                 font=("Helvetica", 18, "bold"),
                 bg=PALETTE["bg"], fg=PALETTE["text"]).pack(pady=(2, 0))
        tk.Label(header, text="Booking Management System",
                 font=("Helvetica", 10),
                 bg=PALETTE["bg"], fg=PALETTE["muted"]).pack()

        # ── Role Selection ───────────────────────────────────────────────────
        role_container = tk.Frame(self, bg=PALETTE["bg"])
        role_container.pack(pady=(20, 0), padx=48, fill="x")

        roles = [
            ("Admin", "🛡️", "admin"),
            ("Manager", "💼", "manager"),
            ("Staff", "🎟️", "staff1")
        ]

        self._role_btns = {}
        for name, icon, uname in roles:
            # Using a Frame + Label approach for better color control on macOS
            f = tk.Frame(role_container, bg=PALETTE["accent2"], padx=1, pady=1)
            f.pack(side="left", expand=True, fill="both", padx=4)

            b = tk.Label(f, 
                        text=f"{icon}\n{name}",
                        font=("Helvetica", 10, "bold"),
                        bg=PALETTE["surface"], fg=PALETTE["text"],
                        padx=10, pady=10,
                        cursor="hand2")
            b.pack(expand=True, fill="both")
            
            # Hover & Click events
            b.bind("<Enter>", lambda e, lbl=b: lbl.config(bg=PALETTE["accent2"], fg="white"))
            b.bind("<Leave>", lambda e, lbl=b: lbl.config(bg=PALETTE["surface"], fg=PALETTE["text"]))
            b.bind("<Button-1>", lambda e, u=uname: self._select_role(u))
            
            self._role_btns[name] = b

        # ── Card ──────────────────────────────────────────────────────────────
        card = tk.Frame(self, bg=PALETTE["surface"],
                        bd=0, highlightthickness=1,
                        highlightbackground=PALETTE["border"])
        card.pack(padx=48, pady=20, fill="x")

        inner = tk.Frame(card, bg=PALETTE["surface"])
        inner.pack(padx=28, pady=20, fill="x")

        tk.Label(inner, text="Sign In", font=FONT_TITLE,
                 bg=PALETTE["surface"], fg=PALETTE["text"]).pack(anchor="w")
        tk.Label(inner, text="Enter your credentials to continue",
                 font=FONT_SUB,
                 bg=PALETTE["surface"], fg=PALETTE["muted"]).pack(anchor="w", pady=(4, 12))

        # Username
        tk.Label(inner, text="Username", font=FONT_LABEL,
                 bg=PALETTE["surface"], fg=PALETTE["muted"]).pack(anchor="w")
        self._username = ttk.Entry(inner, font=FONT_INPUT)
        self._username.pack(fill="x", pady=(2, 12), ipady=6)
        self._username.focus()

        # Password
        tk.Label(inner, text="Password", font=FONT_LABEL,
                 bg=PALETTE["surface"], fg=PALETTE["muted"]).pack(anchor="w")
        self._password = ttk.Entry(inner, show="●", font=FONT_INPUT)
        self._password.pack(fill="x", pady=(2, 16), ipady=6)
        self._password.bind("<Return>", lambda e: self._login())

        # Login button - Custom Frame+Label for consistent Blue
        btn_frame = tk.Frame(inner, bg=PALETTE["accent"])
        btn_frame.pack(fill="x", ipady=0)
        
        btn = tk.Label(btn_frame, text="SIGN IN →",
                      font=("Helvetica", 12, "bold"),
                      bg=PALETTE["accent"], fg="white",
                      cursor="hand2", pady=12)
        btn.pack(fill="x")
        
        btn.bind("<Enter>", lambda e: btn.config(bg=PALETTE["accent2"]))
        btn.bind("<Leave>", lambda e: btn.config(bg=PALETTE["accent"]))
        btn.bind("<Button-1>", lambda e: self._login())

        # Status label
        self._status = tk.Label(inner, text="", font=FONT_LABEL,
                                bg=PALETTE["surface"], fg=PALETTE["accent"])
        self._status.pack(pady=(8, 0))

        # ── Footer ────────────────────────────────────────────────────────────
        tk.Label(self, text="Select a portal to pre-fill or enter credentials manually",
                 font=("Helvetica", 8),
                 bg=PALETTE["bg"], fg=PALETTE["muted"]).pack(pady=(10, 10))

    def _select_role(self, username):
        """Pre-fill username and focus password when a role is clicked."""
        self._username.delete(0, tk.END)
        self._username.insert(0, username)
        
        # We no longer pre-fill the password for security/design preference.
        self._password.delete(0, tk.END)
        self._password.focus()
        self._status.config(text=f"Selected {username.capitalize()} Portal", fg=PALETTE["muted"])

    def _login(self):
        username = self._username.get()
        password = self._password.get()
        try:
            user = AuthController.login(username, password)
            self._status.config(text=f"Welcome, {user.username}!", fg=PALETTE["success"])
            self.after(600, lambda: self._redirect(user))
        except ValueError as e:
            self._status.config(text=str(e), fg=PALETTE["accent"])
            self._password.delete(0, tk.END)

    def _redirect(self, user):
        """Open the correct dashboard based on role, hide the login window."""
        self.withdraw()
        role = user.role

        if role == Role.BOOKING_STAFF:
            from ui.booking_ui import BookingUI
            win = BookingUI(self, user)
        elif role == Role.ADMIN:
            from ui.admin_ui import AdminUI
            win = AdminUI(self, user)
        elif role == Role.MANAGER:
            from ui.manager_ui import ManagerUI
            win = ManagerUI(self, user)
        else:
            messagebox.showerror("Error", f"Unknown role: {role}")
            self.deiconify()
            return

        win.protocol("WM_DELETE_WINDOW", lambda: self._on_child_close(win))

    def show_login(self, win):
        """Called by dashboards to return to the login screen."""
        AuthController.logout()
        if win: win.destroy()
        self._username.delete(0, tk.END)
        self._password.delete(0, tk.END)
        self._status.config(text="")
        self.deiconify()

    def _on_child_close(self, win):
        self.show_login(win)
