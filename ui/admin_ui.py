"""
ui/admin_ui.py — Admin dashboard: manage listings, films, and reports.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from controllers.admin_controller   import AdminController
from controllers.booking_controller import BookingController
from ui.login_ui  import PALETTE, FONT_LABEL, FONT_BUTTON, FONT_INPUT, FONT_TITLE
from ui.cancel_ui import CancelUI


class AdminUI(tk.Toplevel):

    def __init__(self, master, user):
        super().__init__(master)
        self.user  = user
        self._ctrl = AdminController()
        self._bk   = BookingController()
        self.title(f"Horizon Cinemas — Admin [{user.username}]")
        self.geometry("1100x740")
        self.configure(bg=PALETTE["bg"])
        self._build()

    def _build(self):
        # Top bar
        bar = tk.Frame(self, bg=PALETTE["accent2"], pady=8)
        bar.pack(fill="x")
        tk.Label(bar, text="🛠  Admin Dashboard",
                 font=("Helvetica", 13, "bold"),
                 bg=PALETTE["accent2"], fg="white").pack(side="left", padx=16)
        tk.Label(bar, text=f"{self.user.username}  [{self.user.role}]",
                 font=FONT_LABEL,
                 bg=PALETTE["accent2"], fg="#AACCFF").pack(side="right", padx=16)

        # Notebook tabs
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=10)

        self._tab_listings  = tk.Frame(nb, bg=PALETTE["bg"])
        self._tab_bookings  = tk.Frame(nb, bg=PALETTE["bg"])
        self._tab_films     = tk.Frame(nb, bg=PALETTE["bg"])
        self._tab_reports   = tk.Frame(nb, bg=PALETTE["bg"])

        nb.add(self._tab_listings, text="  📅 Listings  ")
        nb.add(self._tab_bookings, text="  🎟 Bookings  ")
        nb.add(self._tab_films,    text="  🎬 Films     ")
        nb.add(self._tab_reports,  text="  📊 Reports   ")

        self._build_listings_tab()
        self._build_bookings_tab()
        self._build_films_tab()
        self._build_reports_tab()

    # ═══════════════════════════════════════════════════════════════════════════
    # LISTINGS TAB
    # ═══════════════════════════════════════════════════════════════════════════

    def _build_listings_tab(self):
        parent = self._tab_listings

        # Toolbar
        tb = tk.Frame(parent, bg=PALETTE["bg"])
        tb.pack(fill="x", pady=(8, 4), padx=8)
        tk.Button(tb, text="➕ Add Listing", font=FONT_BUTTON,
                  bg=PALETTE["success"], fg="white", relief="flat",
                  cursor="hand2", command=self._add_listing_dialog).pack(side="left", padx=(0, 4))
        tk.Button(tb, text="✏️ Edit Selected", font=FONT_BUTTON,
                  bg=PALETTE["accent2"], fg="white", relief="flat",
                  cursor="hand2", command=self._edit_listing_dialog).pack(side="left", padx=4)
        tk.Button(tb, text="🗑 Delete Selected", font=FONT_BUTTON,
                  bg=PALETTE["accent"], fg="white", relief="flat",
                  cursor="hand2", command=self._delete_listing).pack(side="left", padx=4)
        tk.Button(tb, text="🔄 Refresh", font=FONT_BUTTON,
                  bg=PALETTE["accent2"], fg="white", relief="flat",
                  cursor="hand2", command=self._load_listings).pack(side="right")

        # Treeview
        cols = ("ID", "Film", "Cinema", "Date", "Time", "Type", "Screen")
        self._lst_tree = self._make_tree(parent, cols)
        self._load_listings()

    def _load_listings(self):
        tree = self._lst_tree
        tree.delete(*tree.get_children())
        from database.db_manager import db
        rows = db.fetchall(
            """
            SELECT l.listingId, f.title, c.name as cinema,
                   l.showDate, l.showTime, l.showType, s.screenNumber
            FROM listings l
            JOIN films f    ON l.filmId   = f.filmId
            JOIN screens s  ON l.screenId = s.screenId
            JOIN cinemas c  ON s.cinemaId = c.cinemaId
            WHERE l.showDate >= DATE('now')
            ORDER BY l.showDate, l.showTime
            """
        )
        for r in rows:
            tree.insert("", "end", iid=r["listingId"],
                        values=(r["listingId"], r["title"], r["cinema"],
                                r["showDate"], r["showTime"],
                                r["showType"], r["screenNumber"]))

    def _add_listing_dialog(self):
        _ListingDialog(self, self._ctrl, mode="add",
                       on_success=self._load_listings)

    def _edit_listing_dialog(self):
        sel = self._lst_tree.selection()
        if not sel:
            messagebox.showwarning("Select Listing", "Please select a listing first.")
            return
        listing_id = int(sel[0])
        _ListingDialog(self, self._ctrl, mode="edit",
                       listing_id=listing_id, on_success=self._load_listings)

    def _delete_listing(self):
        sel = self._lst_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Please select a listing first.")
            return
        listing_id = int(sel[0])
        if not messagebox.askyesno("Delete Listing",
                                   f"Delete listing #{listing_id}?"):
            return
        try:
            self._ctrl.remove_listing(listing_id)
            self._load_listings()
            messagebox.showinfo("Deleted", "Listing deleted successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ═══════════════════════════════════════════════════════════════════════════
    # BOOKINGS TAB
    # ═══════════════════════════════════════════════════════════════════════════

    def _build_bookings_tab(self):
        parent = self._tab_bookings

        tb = tk.Frame(parent, bg=PALETTE["bg"])
        tb.pack(fill="x", pady=(8, 4), padx=8)
        tk.Button(tb, text="❌ Cancel Selected", font=FONT_BUTTON,
                  bg=PALETTE["accent"], fg="white", relief="flat",
                  cursor="hand2", command=self._cancel_selected).pack(side="left", padx=4)
        tk.Button(tb, text="🔄 Refresh", font=FONT_BUTTON,
                  bg=PALETTE["accent2"], fg="white", relief="flat",
                  cursor="hand2", command=self._load_bookings).pack(side="right")

        cols = ("Ref", "Film", "Date", "Time", "Tickets", "Total", "Status", "Booked On")
        self._bk_tree = self._make_tree(parent, cols)
        self._load_bookings()

    def _load_bookings(self):
        tree = self._bk_tree
        tree.delete(*tree.get_children())
        from database.db_manager import db
        rows = db.fetchall(
            """
            SELECT b.bookingRef, f.title, l.showDate, l.showTime,
                   b.numTickets, b.totalCost, b.status, b.bookingDate
            FROM bookings b
            JOIN listings l ON b.listingId = l.listingId
            JOIN films f    ON l.filmId    = f.filmId
            ORDER BY b.bookingDate DESC
            """
        )
        for r in rows:
            tag = "cancelled" if r["status"] == "Cancelled" else ""
            tree.insert("", "end", iid=r["bookingRef"],
                        values=(r["bookingRef"], r["title"], r["showDate"],
                                r["showTime"], r["numTickets"],
                                f"£{r['totalCost']:.2f}", r["status"],
                                r["bookingDate"]),
                        tags=(tag,))
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

    # ═══════════════════════════════════════════════════════════════════════════
    # FILMS TAB
    # ═══════════════════════════════════════════════════════════════════════════

    def _build_films_tab(self):
        parent = self._tab_films

        tb = tk.Frame(parent, bg=PALETTE["bg"])
        tb.pack(fill="x", pady=(8, 4), padx=8)
        tk.Button(tb, text="➕ Add Film", font=FONT_BUTTON,
                  bg=PALETTE["success"], fg="white", relief="flat",
                  cursor="hand2", command=self._add_film_dialog).pack(side="left")
        tk.Button(tb, text="🔄 Refresh", font=FONT_BUTTON,
                  bg=PALETTE["accent2"], fg="white", relief="flat",
                  cursor="hand2", command=self._load_films).pack(side="right")

        cols = ("ID", "Title", "Genre", "Rating", "Actors")
        self._film_tree = self._make_tree(parent, cols)
        self._load_films()

    def _load_films(self):
        tree = self._film_tree
        tree.delete(*tree.get_children())
        for f in self._ctrl.get_all_films():
            tree.insert("", "end", iid=f.filmId,
                        values=(f.filmId, f.title, f.genre,
                                f.ageRating, f.actors))

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
            ("total_revenue",  "Total Revenue",   "#F39C12"),
            ("total_cancel",   "Cancellations",   PALETTE["accent"]),
            ("total_refunds",  "Total Refunds",   PALETTE["muted"]),
        ]
        for key, label, color in stat_defs:
            card = tk.Frame(stats_frame, bg=PALETTE["surface"],
                            highlightthickness=1,
                            highlightbackground=PALETTE["border"])
            card.pack(side="left", expand=True, fill="x", padx=4)
            val = stats.get(key, 0)
            display = f"£{val:,.2f}" if "revenue" in key or "refund" in key else str(val)
            tk.Label(card, text=display, font=("Helvetica", 18, "bold"),
                     bg=PALETTE["surface"], fg=color).pack(pady=(12, 2))
            tk.Label(card, text=label, font=("Helvetica", 9),
                     bg=PALETTE["surface"], fg=PALETTE["muted"]).pack(pady=(0, 12))
            self._stat_labels[key] = card

        # Report controls
        ctrl_frame = tk.Frame(parent, bg=PALETTE["bg"])
        ctrl_frame.pack(fill="x", padx=8, pady=4)
        tk.Label(ctrl_frame, text="Report Type:", font=FONT_LABEL,
                 bg=PALETTE["bg"], fg=PALETTE["muted"]).pack(side="left")
        self._report_var = tk.StringVar(value="bookings")
        for rt in ["bookings", "revenue", "cancellations", "occupancy"]:
            ttk.Radiobutton(ctrl_frame, text=rt.capitalize(),
                            variable=self._report_var, value=rt).pack(side="left", padx=8)

        tk.Button(ctrl_frame, text="▶ Generate", font=FONT_BUTTON,
                  bg=PALETTE["success"], fg="white", relief="flat",
                  cursor="hand2", command=self._generate_report).pack(side="left", padx=(16, 4))
        tk.Button(ctrl_frame, text="💾 Export CSV", font=FONT_BUTTON,
                  bg=PALETTE["accent2"], fg="white", relief="flat",
                  cursor="hand2", command=self._export_report).pack(side="left")

        # Report treeview
        self._report_tree = ttk.Treeview(parent, show="headings")
        vsb = ttk.Scrollbar(parent, orient="vertical",
                            command=self._report_tree.yview)
        hsb = ttk.Scrollbar(parent, orient="horizontal",
                            command=self._report_tree.xview)
        self._report_tree.configure(yscrollcommand=vsb.set,
                                    xscrollcommand=hsb.set)
        hsb.pack(side="bottom", fill="x", padx=8)
        vsb.pack(side="right",  fill="y", pady=(0, 8))
        self._report_tree.pack(fill="both", expand=True, padx=(8, 0), pady=(4, 0))
        self._last_report = None

    def _generate_report(self):
        rtype  = self._report_var.get()
        report = self._ctrl.generate_report(rtype)
        self._last_report = report
        tree   = self._report_tree

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
        vsb = ttk.Scrollbar(frame, orient="vertical",   command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        hsb.pack(side="bottom", fill="x")
        vsb.pack(side="right",  fill="y")
        tree.pack(fill="both", expand=True)
        return tree


# ── Helper dialogs ────────────────────────────────────────────────────────────

class _ListingDialog(tk.Toplevel):
    """Add or Edit a Listing."""

    def __init__(self, master, ctrl, mode="add",
                 listing_id=None, on_success=None):
        super().__init__(master)
        self._ctrl       = ctrl
        self._mode       = mode
        self._listing_id = listing_id
        self._on_success = on_success
        self.title("Add Listing" if mode == "add" else "Edit Listing")
        self.geometry("440px x 400px".replace("px", "").replace(" ", ""))
        self.geometry("440x400")
        self.resizable(False, False)
        self.configure(bg=PALETTE["bg"])
        self._build()
        if mode == "edit" and listing_id:
            self._prefill()

    def _build(self):
        inner = tk.Frame(self, bg=PALETTE["bg"])
        inner.pack(padx=24, pady=20, fill="both", expand=True)

        fields = [
            ("Film",       "_film_var",   "combobox"),
            ("Screen",     "_screen_var", "combobox"),
            ("Date (YYYY-MM-DD)", "_date_var", "entry"),
            ("Time (HH:MM)",     "_time_var", "entry"),
            ("Show Type",  "_type_var",   "combobox"),
        ]
        self._films   = self._ctrl.get_all_films()
        self._screens = self._ctrl.get_all_screens()

        film_labels   = [f.title for f in self._films]
        screen_labels = [
            f"{r['cinemaName']} — Screen {r['screenNumber']} ({r['city']})"
            for r in self._screens
        ]
        show_types = ["Standard", "IMAX", "3D", "Directors"]

        for i, (label, attr, kind) in enumerate(fields):
            tk.Label(inner, text=label, font=FONT_LABEL,
                     bg=PALETTE["bg"], fg=PALETTE["muted"]).grid(
                row=i, column=0, sticky="w", pady=6)
            var = tk.StringVar()
            setattr(self, attr, var)
            if kind == "combobox":
                values = (film_labels   if "film" in attr else
                          screen_labels if "screen" in attr else
                          show_types)
                cb = ttk.Combobox(inner, textvariable=var,
                                  values=values, state="readonly",
                                  font=FONT_INPUT, width=30)
                cb.grid(row=i, column=1, padx=(12, 0), pady=6, sticky="ew")
            else:
                ttk.Entry(inner, textvariable=var,
                          font=FONT_INPUT, width=32).grid(
                    row=i, column=1, padx=(12, 0), pady=6, sticky="ew")

        self._status = tk.Label(inner, text="", font=FONT_LABEL,
                                bg=PALETTE["bg"], fg=PALETTE["accent"],
                                wraplength=380)
        self._status.grid(row=len(fields), column=0, columnspan=2, pady=(8, 0))

        tk.Button(inner, text="Save",
                  font=FONT_BUTTON, bg=PALETTE["success"],
                  fg="white", relief="flat", cursor="hand2",
                  command=self._save).grid(
            row=len(fields)+1, column=0, columnspan=2,
            sticky="ew", pady=(12, 0), ipady=6)

    def _prefill(self):
        from models.listing import Listing
        lst = Listing.get_by_id(self._listing_id)
        if not lst:
            return
        film   = next((f for f in self._films if f.filmId == lst.filmId), None)
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
                (s for s in self._screens
                 if f"{s['cinemaName']} — Screen {s['screenNumber']} ({s['city']})" == screen_label),
                None
            )
            if not screen:
                raise Exception("Please select a screen.")

            if self._mode == "add":
                self._ctrl.add_listing(
                    film.filmId, screen["screenId"],
                    self._date_var.get(), self._time_var.get(),
                    self._type_var.get(),
                )
            else:
                self._ctrl.update_listing(
                    self._listing_id,
                    film_id=film.filmId, screen_id=screen["screenId"],
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
        self._ctrl       = ctrl
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
        for i, (label, key) in enumerate([
            ("Title",       "title"),
            ("Description", "description"),
            ("Genre",       "genre"),
            ("Age Rating",  "age_rating"),
            ("Actors",      "actors"),
        ]):
            tk.Label(inner, text=label, font=FONT_LABEL,
                     bg=PALETTE["bg"], fg=PALETTE["muted"]).grid(
                row=i, column=0, sticky="w", pady=6)
            var = tk.StringVar()
            self._vars[key] = var
            ttk.Entry(inner, textvariable=var,
                      font=FONT_INPUT, width=32).grid(
                row=i, column=1, padx=(12, 0), pady=6, sticky="ew")

        self._status = tk.Label(inner, text="", font=FONT_LABEL,
                                bg=PALETTE["bg"], fg=PALETTE["accent"])
        self._status.grid(row=5, column=0, columnspan=2, pady=(8, 0))

        tk.Button(inner, text="Add Film",
                  font=FONT_BUTTON, bg=PALETTE["success"],
                  fg="white", relief="flat", cursor="hand2",
                  command=self._save).grid(
            row=6, column=0, columnspan=2,
            sticky="ew", pady=(12, 0), ipady=6)

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
