# Author: StudyingBelial | Student ID: 1234567
# Module: UFCF8S-30-2 Advanced Software Development

"""
ui/admin_ui.py — Admin dashboard: manage listings, films, and reports.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from controllers.admin_controller import AdminController
from controllers.booking_controller import BookingController
from ui.login_ui import PALETTE, FONT_LABEL, FONT_BUTTON, FONT_INPUT, FONT_TITLE
from ui.cancel_ui import CancelUI


class AdminUI(tk.Toplevel):

    def __init__(self, master, user):
        super().__init__(master)
        self.user = user
        self._ctrl = AdminController()
        self._bk = BookingController()
        self.title(f"Horizon Cinemas — Admin [{user.username}]")
        self.geometry("1100x740")
        self.configure(bg=PALETTE["bg"])
        style = ttk.Style(self)
        style.theme_use("clam")  # needed to allow field background customisation
        style.configure(
            "TCombobox",
            fieldbackground=PALETTE["surface"],
            background=PALETTE["surface"],
            foreground=PALETTE["text"],
            selectbackground=PALETTE["accent2"],
            selectforeground="white",
            arrowcolor=PALETTE["text"],
            )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", PALETTE["surface"])],
            foreground=[("readonly", PALETTE["text"])],
            selectbackground=[("readonly", PALETTE["accent2"])],
            selectforeground=[("readonly", "white")],
)
        self._build()

    def _build(self):
        # Top bar
        bar = tk.Frame(self, bg=PALETTE["accent2"], pady=8)
        bar.pack(fill="x")
        tk.Label(
            bar,
            text="🛠  Admin Dashboard",
            font=("Helvetica", 13, "bold"),
            bg=PALETTE["accent2"],
            fg="white",
        ).pack(side="left", padx=16)
        tk.Label(
            bar,
            text=f"{self.user.username}  [{self.user.role}]",
            font=FONT_LABEL,
            bg=PALETTE["accent2"],
            fg="#AACCFF",
        ).pack(side="right", padx=(16, 8))

        # Custom Logout button
        log_b = tk.Button(
            bar,
            text="Logout 🚪",
            font=("Helvetica", 9, "bold"),
            bg="#E94560",
            fg="white",
            cursor="hand2",
            relief="flat",
            activebackground="#C0392B",
            activeforeground="white",
            command=lambda: self.master.show_login(self),
        )
        log_b.pack(side="right", padx=16, pady=4)

        # Notebook tabs
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=10)

        self._tab_listings = tk.Frame(nb, bg=PALETTE["bg"])
        self._tab_bookings = tk.Frame(nb, bg=PALETTE["bg"])
        self._tab_films = tk.Frame(nb, bg=PALETTE["bg"])
        self._tab_reports = tk.Frame(nb, bg=PALETTE["bg"])

        nb.add(self._tab_listings, text="  📅 Listings  ")
        nb.add(self._tab_bookings, text="  🎟 Bookings  ")
        nb.add(self._tab_films, text="  🎬 Films     ")
        nb.add(self._tab_reports, text="  📊 Reports   ")

        self._build_listings_tab()
        self._build_bookings_tab()
        self._build_films_tab()
        self._build_reports_tab()

    # ═══════════════════════════════════════════════════════════════════════════
    # LISTINGS TAB
    # ═══════════════════════════════════════════════════════════════════════════

    def _btn(self, parent, text, command, bg=None, side="left", padx=4):
        """Helper to create native Windows buttons."""
        color = bg if bg else PALETTE["accent"]
        b = tk.Button(
            parent,
            text=text,
            command=command,
            font=FONT_BUTTON,
            bg=color,
            fg="white",
            cursor="hand2",
            relief="flat",
            activebackground=PALETTE["accent2"],
            activeforeground="white",
            padx=8,
            pady=2,
        )
        b.pack(side=side, padx=padx)
        return b

    def _build_listings_tab(self):
        parent = self._tab_listings

        # Toolbar
        tb = tk.Frame(parent, bg=PALETTE["bg"])
        tb.pack(fill="x", pady=(8, 4), padx=8)

        self._btn(tb, "➕ Add Listing", self._add_listing_dialog, bg="#2ECC71")
        self._btn(
            tb, "✏️ Edit Selected", self._edit_listing_dialog, bg=PALETTE["accent2"]
        )
        self._btn(tb, "🗑 Delete Selected", self._delete_listing, bg=PALETTE["accent"])
        self._btn(tb, "🎟 Book Selected", self._book_selected, bg="#F39C12")
        self._btn(
            tb, "🔄 Refresh", self._load_listings, bg=PALETTE["accent2"], side="right"
        )

        # Treeview
        cols = ("ID", "Film", "Cinema", "Date", "Time", "Type", "Screen")
        self._lst_tree = self._make_tree(parent, cols)
        self._load_listings()

    def _load_listings(self):
        tree = self._lst_tree
        tree.delete(*tree.get_children())
        from database.db_manager import db

        rows = db.fetchall("""
            SELECT l.listingId, f.title, c.name as cinema,
                   l.showDate, l.showTime, l.showType, s.screenNumber
            FROM listings l
            JOIN films f    ON l.filmId   = f.filmId
            JOIN screens s  ON l.screenId = s.screenId
            JOIN cinemas c  ON s.cinemaId = c.cinemaId
            WHERE l.showDate >= DATE('now')
            ORDER BY l.showDate, l.showTime
            """)
        for r in rows:
            tree.insert(
                "",
                "end",
                iid=r["listingId"],
                values=(
                    r["listingId"],
                    r["title"],
                    r["cinema"],
                    r["showDate"],
                    r["showTime"],
                    r["showType"],
                    r["screenNumber"],
                ),
            )

    def _add_listing_dialog(self):
        _ListingDialog(self, self._ctrl, mode="add", on_success=self._load_listings)

    def _edit_listing_dialog(self):
        sel = self._lst_tree.selection()
        if not sel:
            messagebox.showwarning("Select Listing", "Please select a listing first.")
            return
        listing_id = int(sel[0])
        _ListingDialog(
            self,
            self._ctrl,
            mode="edit",
            listing_id=listing_id,
            on_success=self._load_listings,
        )

    def _delete_listing(self):
        sel = self._lst_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Please select a listing first.")
            return
        listing_id = int(sel[0])
        if not messagebox.askyesno("Delete Listing", f"Delete listing #{listing_id}?"):
            return
        try:
            self._ctrl.remove_listing(listing_id)
            self._load_listings()
            messagebox.showinfo("Deleted", "Listing deleted successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _book_selected(self):
        sel = self._lst_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Please select a listing first.")
            return
        listing_id = int(sel[0])
        from ui.booking_ui import BookingUI
        # Pass the LoginUI (master of AdminUI) as the master for BookingUI
        win = BookingUI(self.master, self.user)
        # Optionally pre-select the listing if we add that feature to BookingUI
        # For now, just opening the UI is a huge step.

    # ═══════════════════════════════════════════════════════════════════════════
    # BOOKINGS TAB
    # ═══════════════════════════════════════════════════════════════════════════

    def _build_bookings_tab(self):
        parent = self._tab_bookings

        tb = tk.Frame(parent, bg=PALETTE["bg"])
        tb.pack(fill="x", pady=(8, 4), padx=8)
        self._btn(tb, "➕ New Booking", self._new_booking, bg="#2ECC71")
        self._btn(tb, "❌ Cancel Booking", self._open_cancel_dialog, bg=PALETTE["accent"])
        self._btn(
            tb, "🔄 Refresh", self._load_bookings, bg=PALETTE["accent2"], side="right"
        )

        cols = (
            "Ref",
            "Film",
            "Date",
            "Time",
            "Tickets",
            "Total",
            "Status",
            "Booked On",
        )
        self._bk_tree = self._make_tree(parent, cols)
        self._load_bookings()

    def _load_bookings(self):
        tree = self._bk_tree
        tree.delete(*tree.get_children())
        from database.db_manager import db

        rows = db.fetchall("""
            SELECT b.bookingRef, f.title, l.showDate, l.showTime,
                   b.numTickets, b.totalCost, b.status, b.bookingDate
            FROM bookings b
            JOIN listings l ON b.listingId = l.listingId
            JOIN films f    ON l.filmId    = f.filmId
            ORDER BY b.bookingDate DESC
            """)
        for r in rows:
            tag = "cancelled" if r["status"] == "Cancelled" else ""
            tree.insert(
                "",
                "end",
                iid=r["bookingRef"],
                values=(
                    r["bookingRef"],
                    r["title"],
                    r["showDate"],
                    r["showTime"],
                    r["numTickets"],
                    f"£{r['totalCost']:.2f}",
                    r["status"],
                    r["bookingDate"],
                ),
                tags=(tag,),
            )
        tree.tag_configure("cancelled", foreground=PALETTE["muted"])

    def _cancel_selected(self):
        sel = self._bk_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Please select a booking first.")
            return
        ref = sel[0]
        if not messagebox.askyesno("Cancel Booking", f"Cancel booking {ref}?"):
            return
        try:
            result = self._bk.cancel_booking(ref)
            messagebox.showinfo("Cancelled", result["message"])
            self._load_bookings()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _new_booking(self):
        from ui.booking_ui import BookingUI
        BookingUI(self.master, self.user)

    def _open_cancel_dialog(self):
        from ui.cancel_ui import CancelUI
        CancelUI(self.master)

    # ═══════════════════════════════════════════════════════════════════════════
    # FILMS TAB
    # ═══════════════════════════════════════════════════════════════════════════

    def _build_films_tab(self):
        parent = self._tab_films

        tb = tk.Frame(parent, bg=PALETTE["bg"])
        tb.pack(fill="x", pady=(8, 4), padx=8)
        self._btn(tb, "➕ Add Film", self._add_film_dialog, bg="#2ECC71")
        self._btn(
            tb, "🔄 Refresh", self._load_films, bg=PALETTE["accent2"], side="right"
        )

        cols = ("ID", "Title", "Genre", "Rating", "Actors")
        self._film_tree = self._make_tree(parent, cols)
        self._load_films()

    def _load_films(self):
        tree = self._film_tree
        tree.delete(*tree.get_children())
        for f in self._ctrl.get_all_films():
            tree.insert(
                "",
                "end",
                iid=f.filmId,
                values=(f.filmId, f.title, f.genre, f.ageRating, f.actors),
            )

    def _add_film_dialog(self):
        _FilmDialog(self, self._ctrl, on_success=self._load_films)

    # ═══════════════════════════════════════════════════════════════════════════
    # REPORTS TAB
    # ═══════════════════════════════════════════════════════════════════════════

    def _build_reports_tab(self):
        parent = self._tab_reports

        # Stats row
        stats_frame = tk.Frame(parent, bg=PALETTE["bg"])
        stats_frame.pack(fill="x", padx=8, pady=(12, 8))
        self._stat_labels = {}
        stats = self._ctrl.get_summary_stats()
        stat_defs = [
            ("total_bookings", "Active Bookings", PALETTE["success"]),
            ("total_revenue", "Total Revenue", "#F39C12"),
            ("total_cancel", "Cancellations", PALETTE["accent"]),
            ("total_refunds", "Total Refunds", PALETTE["muted"]),
        ]
        for key, label, color in stat_defs:
            card = tk.Frame(
                stats_frame,
                bg=PALETTE["surface"],
                highlightthickness=1,
                highlightbackground=PALETTE["border"],
            )
            card.pack(side="left", expand=True, fill="x", padx=4)
            val = stats.get(key, 0)
            display = (
                f"£{val:,.2f}" if "revenue" in key or "refund" in key else str(val)
            )
            tk.Label(
                card,
                text=display,
                font=("Helvetica", 18, "bold"),
                bg=PALETTE["surface"],
                fg=color,
            ).pack(pady=(12, 2))
            tk.Label(
                card,
                text=label,
                font=("Helvetica", 9),
                bg=PALETTE["surface"],
                fg=PALETTE["muted"],
            ).pack(pady=(0, 12))
            self._stat_labels[key] = card

        # Report controls
        ctrl_frame = tk.Frame(parent, bg=PALETTE["bg"])
        ctrl_frame.pack(fill="x", padx=8, pady=4)
        tk.Label(
            ctrl_frame,
            text="Report Type:",
            font=FONT_LABEL,
            bg=PALETTE["bg"],
            fg=PALETTE["muted"],
        ).pack(side="left")
        self._report_var = tk.StringVar(value="bookings")

        report_types = [
            ("Bookings", "bookings"),
            ("Revenue", "revenue"),
            ("Cancellations", "cancellations"),
            ("Occupancy", "occupancy"),
            ("Top Film", "top_film"),
            ("Staff", "staff_bookings"),
        ]
        for label, val in report_types:
            ttk.Radiobutton(
                ctrl_frame, text=label, variable=self._report_var, value=val
            ).pack(side="left", padx=8)

        # Month filter
        tk.Label(
            ctrl_frame,
            text="Month (YYYY-MM):",
            font=FONT_LABEL,
            bg=PALETTE["bg"],
            fg=PALETTE["muted"],
        ).pack(side="left", padx=(16, 4))
        self._month_var = tk.StringVar()
        ttk.Entry(ctrl_frame, textvariable=self._month_var, width=10).pack(side="left")

        self._btn(ctrl_frame, "▶ Generate", self._generate_report, bg="#2ECC71")
        self._btn(
            ctrl_frame, "💾 Export CSV", self._export_report, bg=PALETTE["accent2"]
        )

        # Report treeview
        self._report_tree = ttk.Treeview(parent, show="headings")
        vsb = ttk.Scrollbar(parent, orient="vertical", command=self._report_tree.yview)
        hsb = ttk.Scrollbar(
            parent, orient="horizontal", command=self._report_tree.xview
        )
        self._report_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        hsb.pack(side="bottom", fill="x", padx=8)
        vsb.pack(side="right", fill="y", pady=(0, 8))
        self._report_tree.pack(fill="both", expand=True, padx=(8, 0), pady=(4, 0))
        self._last_report = None

    def _generate_report(self):
        try:
            rtype = self._report_var.get()
            month = self._month_var.get() or None
            report = self._ctrl.generate_report(rtype, month=month)
            self._last_report = report
            tree = self._report_tree

            if not report.data:
                messagebox.showinfo("Empty", "No data for this report.")
                return

            # Configure columns
            cols = list(report.data[0].keys())
            tree["columns"] = cols
            for col in cols:
                tree.heading(col, text=col.replace("_", " ").title())
                tree.column(col, width=130, minwidth=80)

            tree.delete(*tree.get_children())
            for row in report.data:
                tree.insert("", "end", values=list(row.values()))
        except Exception as e:
            messagebox.showerror("Report Error", f"Failed to generate report: {str(e)}")

    def _export_report(self):
        if not self._last_report:
            messagebox.showwarning("No Report", "Generate a report first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save Report As",
        )
        if path:
            self._last_report.export(path)
            messagebox.showinfo("Exported", f"Report saved to:\n{path}")

    # ── Helper ─────────────────────────────────────────────────────────────────

    def _make_tree(self, parent, cols):
        frame = tk.Frame(parent, bg=PALETTE["bg"])
        frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        tree = ttk.Treeview(frame, columns=cols, show="headings")
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=120, minwidth=60)
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        hsb.pack(side="bottom", fill="x")
        vsb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)
        return tree


# ── Helper dialogs ────────────────────────────────────────────────────────────


class _ListingDialog(tk.Toplevel):
    """Add or Edit a Listing."""

    def __init__(self, master, ctrl, mode="add", listing_id=None, on_success=None):
        super().__init__(master)
        self._ctrl = ctrl
        self._mode = mode
        self._listing_id = listing_id
        self._on_success = on_success

        # Initialize variables before building UI
        self._film_var = tk.StringVar()
        self._screen_var = tk.StringVar()
        self._date_var = tk.StringVar()
        self._time_var = tk.StringVar()
        self._type_var = tk.StringVar()

        self.title("Add Listing" if mode == "add" else "Edit Listing")
        self.geometry("440x400")
        self.resizable(False, False)
        self.configure(bg=PALETTE["bg"])
        self._build()
        if mode == "edit" and listing_id:
            self._prefill()

    def _build(self):
        inner = tk.Frame(self, bg=PALETTE["bg"])
        inner.pack(padx=24, pady=20, fill="both", expand=True)

        self._films = self._ctrl.get_all_films()
        self._screens = self._ctrl.get_all_screens()

        film_labels = [f.title for f in self._films]
        screen_labels = [
            f"{r['cinemaName']} — Screen {r['screenNumber']} ({r['city']})"
            for r in self._screens
        ]
        show_types = ["Standard", "IMAX", "3D", "Directors"]

        def add_row(row, label, var, kind, values=None):
            tk.Label(
                inner,
                text=label,
                font=FONT_LABEL,
                bg=PALETTE["bg"],
                fg=PALETTE["muted"],
            ).grid(row=row, column=0, sticky="w", pady=6)

            if kind == "combobox":
                cb = ttk.Combobox(
                    inner,
                    textvariable=var,
                    values=values,
                    state="readonly",
                    font=FONT_INPUT,
                    width=30,
                )
                cb.grid(row=row, column=1, padx=(12, 0), pady=6, sticky="ew")
            else:
                ent = ttk.Entry(inner, textvariable=var, font=FONT_INPUT, width=32)
                ent.grid(row=row, column=1, padx=(12, 0), pady=6, sticky="ew")

        add_row(0, "Film", self._film_var, "combobox", film_labels)
        add_row(1, "Screen", self._screen_var, "combobox", screen_labels)
        add_row(2, "Date (YYYY-MM-DD)", self._date_var, "entry")
        add_row(3, "Time (HH:MM)", self._time_var, "entry")
        add_row(4, "Show Type", self._type_var, "combobox", show_types)

        self._status = tk.Label(
            inner,
            text="",
            font=FONT_LABEL,
            bg=PALETTE["bg"],
            fg=PALETTE["accent"],
            wraplength=380,
        )
        self._status.grid(row=5, column=0, columnspan=2, pady=(8, 0))

        # Custom Save button
        btn_f = tk.Frame(inner, bg=PALETTE["success"])
        btn_f.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        btn = tk.Label(
            btn_f,
            text="SAVE",
            font=FONT_BUTTON,
            bg=PALETTE["success"],
            fg="white",
            cursor="hand2",
            pady=10,
        )
        btn.pack(fill="x")
        btn.bind("<Enter>", lambda e: btn.config(bg="#27ae60"))
        btn.bind("<Leave>", lambda e: btn.config(bg=PALETTE["success"]))
        btn.bind("<Button-1>", lambda e: self._save())

    def _prefill(self):
        from models.listing import Listing

        lst = Listing.get_by_id(self._listing_id)
        if not lst:
            return
        film = next((f for f in self._films if f.filmId == lst.filmId), None)
        screen = next((s for s in self._screens if s["screenId"] == lst.screenId), None)
        if film:
            self._film_var.set(film.title)
        if screen:
            self._screen_var.set(
                f"{screen['cinemaName']} — Screen {screen['screenNumber']} ({screen['city']})"
            )
        self._date_var.set(lst.showDate)
        self._time_var.set(lst.showTime)
        self._type_var.set(lst.showType)

    def _save(self):
        try:
            film_title = self._film_var.get()
            film = next((f for f in self._films if f.title == film_title), None)
            if not film:
                raise Exception("Please select a film.")

            screen_label = self._screen_var.get()
            screen = next(
                (
                    s
                    for s in self._screens
                    if f"{s['cinemaName']} — Screen {s['screenNumber']} ({s['city']})"
                    == screen_label
                ),
                None,
            )
            if not screen:
                raise Exception("Please select a screen.")

            if self._mode == "add":
                self._ctrl.add_listing(
                    film.filmId,
                    screen["screenId"],
                    self._date_var.get(),
                    self._time_var.get(),
                    self._type_var.get(),
                )
            else:
                self._ctrl.update_listing(
                    self._listing_id,
                    film_id=film.filmId,
                    screen_id=screen["screenId"],
                    show_date=self._date_var.get(),
                    show_time=self._time_var.get(),
                    show_type=self._type_var.get(),
                )
            if self._on_success:
                self._on_success()
            self.destroy()
        except Exception as e:
            self._status.config(text=str(e))


class _FilmDialog(tk.Toplevel):
    """Add a new Film."""

    def __init__(self, master, ctrl, on_success=None):
        super().__init__(master)
        self._ctrl = ctrl
        self._on_success = on_success
        self.title("Add Film")
        self.geometry("420x380")
        self.resizable(False, False)
        self.configure(bg=PALETTE["bg"])
        self._build()

    def _build(self):
        inner = tk.Frame(self, bg=PALETTE["bg"])
        inner.pack(padx=24, pady=20, fill="both", expand=True)

        self._vars = {}
        for i, (label, key) in enumerate(
            [
                ("Title", "title"),
                ("Description", "description"),
                ("Genre", "genre"),
                ("Age Rating", "age_rating"),
                ("Actors", "actors"),
            ]
        ):
            tk.Label(
                inner,
                text=label,
                font=FONT_LABEL,
                bg=PALETTE["bg"],
                fg=PALETTE["muted"],
            ).grid(row=i, column=0, sticky="w", pady=6)
            var = tk.StringVar()
            self._vars[key] = var
            ttk.Entry(inner, textvariable=var, font=FONT_INPUT, width=32).grid(
                row=i, column=1, padx=(12, 0), pady=6, sticky="ew"
            )

        self._status = tk.Label(
            inner, text="", font=FONT_LABEL, bg=PALETTE["bg"], fg=PALETTE["accent"]
        )
        self._status.grid(row=5, column=0, columnspan=2, pady=(8, 0))

        # Custom Add Film button
        btn_f = tk.Frame(inner, bg=PALETTE["success"])
        btn_f.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        btn = tk.Label(
            btn_f,
            text="ADD FILM",
            font=FONT_BUTTON,
            bg=PALETTE["success"],
            fg="white",
            cursor="hand2",
            pady=10,
        )
        btn.pack(fill="x")
        btn.bind("<Enter>", lambda e: btn.config(bg="#27ae60"))
        btn.bind("<Leave>", lambda e: btn.config(bg=PALETTE["success"]))
        btn.bind("<Button-1>", lambda e: self._save())

    def _save(self):
        try:
            film_id = self._ctrl.add_film(
                self._vars["title"].get(),
                self._vars["description"].get(),
                self._vars["genre"].get(),
                self._vars["age_rating"].get(),
                self._vars["actors"].get(),
            )
            if self._on_success:
                self._on_success()
            messagebox.showinfo("Added", f"Film added with ID #{film_id}")
            self.destroy()
        except Exception as e:
            self._status.config(text=str(e))
