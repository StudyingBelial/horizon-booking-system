"""
ui/manager_ui.py — Manager dashboard: cinemas, cities, staff, pricing, reports.
Managers inherit all Admin capabilities plus system configuration.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from controllers.manager_controller import ManagerController
from controllers.admin_controller   import AdminController
from ui.login_ui import PALETTE, FONT_LABEL, FONT_BUTTON, FONT_INPUT


class ManagerUI(tk.Toplevel):

    def __init__(self, master, user):
        super().__init__(master)
        self.user   = user
        self._ctrl  = ManagerController()
        self._admin = AdminController()
        self.title(f"Horizon Cinemas — Manager [{user.username}]")
        self.geometry("1100x760")
        self.configure(bg=PALETTE["bg"])
        self._build()

    def _build(self):
        # Top bar
        bar = tk.Frame(self, bg="#0F3460", pady=8)
        bar.pack(fill="x")
        tk.Label(bar, text="👑  Manager Dashboard",
                 font=("Helvetica", 13, "bold"),
                 bg="#0F3460", fg="white").pack(side="left", padx=16)
        tk.Label(bar, text=f"{self.user.username}  [{self.user.role}]",
                 font=FONT_LABEL,
                 bg="#0F3460", fg="#AACCFF").pack(side="right", padx=16)

        # Stats strip
        self._build_stats_strip()

        # Notebook
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=(4, 10))

        self._tab_cinemas  = tk.Frame(nb, bg=PALETTE["bg"])
        self._tab_cities   = tk.Frame(nb, bg=PALETTE["bg"])
        self._tab_staff    = tk.Frame(nb, bg=PALETTE["bg"])
        self._tab_pricing  = tk.Frame(nb, bg=PALETTE["bg"])
        self._tab_reports  = tk.Frame(nb, bg=PALETTE["bg"])

        nb.add(self._tab_cinemas, text="  🏛 Cinemas   ")
        nb.add(self._tab_cities,  text="  🌍 Cities    ")
        nb.add(self._tab_staff,   text="  👤 Staff     ")
        nb.add(self._tab_pricing, text="  💰 Pricing   ")
        nb.add(self._tab_reports, text="  📊 Reports   ")

        self._build_cinemas_tab()
        self._build_cities_tab()
        self._build_staff_tab()
        self._build_pricing_tab()
        self._build_reports_tab()

    def _build_stats_strip(self):
        strip = tk.Frame(self, bg=PALETTE["bg"])
        strip.pack(fill="x", padx=10, pady=(8, 0))
        stats = self._ctrl.get_summary_stats()
        defs  = [
            ("total_bookings", "Active Bookings", PALETTE["success"]),
            ("total_revenue",  "Revenue",         "#F39C12"),
            ("total_cancel",   "Cancellations",   PALETTE["accent"]),
            ("total_films",    "Films",            PALETTE["accent2"]),
            ("total_cinemas",  "Cinemas",          "#9B59B6"),
        ]
        for key, label, color in defs:
            card = tk.Frame(strip, bg=PALETTE["surface"],
                            highlightthickness=1,
                            highlightbackground=PALETTE["border"])
            card.pack(side="left", expand=True, fill="x", padx=3)
            val = stats.get(key, 0)
            display = f"£{val:,.2f}" if "revenue" in key else str(val)
            tk.Label(card, text=display, font=("Helvetica", 16, "bold"),
                     bg=PALETTE["surface"], fg=color).pack(pady=(10, 2))
            tk.Label(card, text=label, font=("Helvetica", 8),
                     bg=PALETTE["surface"], fg=PALETTE["muted"]).pack(pady=(0, 10))

    # ═══════════════════════════════════════════════════════════════════════════
    # CINEMAS TAB
    # ═══════════════════════════════════════════════════════════════════════════

    def _build_cinemas_tab(self):
        parent = self._tab_cinemas

        tb = tk.Frame(parent, bg=PALETTE["bg"])
        tb.pack(fill="x", pady=(8, 4), padx=8)
        tk.Button(tb, text="➕ Add Cinema", font=FONT_BUTTON,
                  bg=PALETTE["success"], fg="white", relief="flat",
                  cursor="hand2", command=self._add_cinema_dialog).pack(side="left", padx=4)
        tk.Button(tb, text="➕ Add Screen", font=FONT_BUTTON,
                  bg=PALETTE["accent2"], fg="white", relief="flat",
                  cursor="hand2", command=self._add_screen_dialog).pack(side="left", padx=4)
        tk.Button(tb, text="🔄 Refresh", font=FONT_BUTTON,
                  bg=PALETTE["accent2"], fg="white", relief="flat",
                  cursor="hand2", command=self._load_cinemas).pack(side="right")

        cols = ("ID", "Name", "City", "Address", "Screens")
        self._cinema_tree = self._make_tree(parent, cols)
        self._load_cinemas()

    def _load_cinemas(self):
        tree = self._cinema_tree
        tree.delete(*tree.get_children())
        from database.db_manager import db
        rows = db.fetchall(
            """
            SELECT c.cinemaId, c.name, c.city, c.address,
                   COUNT(s.screenId) as screens
            FROM cinemas c
            LEFT JOIN screens s ON s.cinemaId = c.cinemaId
            GROUP BY c.cinemaId
            ORDER BY c.city, c.name
            """
        )
        for r in rows:
            tree.insert("", "end", values=(r["cinemaId"], r["name"],
                                           r["city"], r["address"],
                                           r["screens"]))

    def _add_cinema_dialog(self):
        _FormDialog(self, title="Add Cinema",
                    fields=[("Name", "name"), ("City", "city"),
                            ("Address", "address")],
                    on_submit=lambda v: self._ctrl.add_cinema(
                        v["name"], v["city"], v["address"]
                    ),
                    on_success=self._load_cinemas)

    def _add_screen_dialog(self):
        _FormDialog(self, title="Add Screen to Cinema",
                    fields=[
                        ("Cinema ID", "cinema_id"),
                        ("Screen Number", "screen_number"),
                        ("Total Capacity", "total_capacity"),
                        ("Lower Hall Seats", "lower_seats"),
                        ("Upper Gallery Seats", "upper_seats"),
                    ],
                    on_submit=lambda v: self._ctrl.add_screen(
                        int(v["cinema_id"]), int(v["screen_number"]),
                        int(v["total_capacity"]),
                        int(v["lower_seats"]), int(v["upper_seats"]),
                    ),
                    on_success=self._load_cinemas)

    # ═══════════════════════════════════════════════════════════════════════════
    # CITIES TAB
    # ═══════════════════════════════════════════════════════════════════════════

    def _build_cities_tab(self):
        parent = self._tab_cities

        tb = tk.Frame(parent, bg=PALETTE["bg"])
        tb.pack(fill="x", pady=(8, 4), padx=8)
        tk.Button(tb, text="➕ Add City", font=FONT_BUTTON,
                  bg=PALETTE["success"], fg="white", relief="flat",
                  cursor="hand2", command=self._add_city_dialog).pack(side="left")
        tk.Button(tb, text="🔄 Refresh", font=FONT_BUTTON,
                  bg=PALETTE["accent2"], fg="white", relief="flat",
                  cursor="hand2", command=self._load_cities).pack(side="right")

        cols = ("City", "Standard", "IMAX", "3D", "Directors")
        self._city_tree = self._make_tree(parent, cols)
        self._load_cities()

    def _load_cities(self):
        tree = self._city_tree
        tree.delete(*tree.get_children())
        from database.db_manager import db
        cities = self._ctrl.get_all_cities()
        for city in cities:
            prices = {}
            for st in ["Standard", "IMAX", "3D", "Directors"]:
                row = db.fetchone(
                    "SELECT basePrice FROM pricing_rules WHERE city=? AND showType=?",
                    (city, st)
                )
                prices[st] = f"£{row['basePrice']:.2f}" if row else "N/A"
            tree.insert("", "end", values=(
                city, prices["Standard"], prices["IMAX"],
                prices["3D"], prices["Directors"]
            ))

    def _add_city_dialog(self):
        _FormDialog(self, title="Add New City",
                    fields=[("City Name", "city_name")],
                    on_submit=lambda v: self._ctrl.add_city(v["city_name"]),
                    on_success=self._load_cities)

    # ═══════════════════════════════════════════════════════════════════════════
    # STAFF TAB
    # ═══════════════════════════════════════════════════════════════════════════

    def _build_staff_tab(self):
        parent = self._tab_staff

        tb = tk.Frame(parent, bg=PALETTE["bg"])
        tb.pack(fill="x", pady=(8, 4), padx=8)
        tk.Button(tb, text="➕ Add Staff", font=FONT_BUTTON,
                  bg=PALETTE["success"], fg="white", relief="flat",
                  cursor="hand2", command=self._add_staff_dialog).pack(side="left", padx=4)
        tk.Button(tb, text="🗑 Remove Selected", font=FONT_BUTTON,
                  bg=PALETTE["accent"], fg="white", relief="flat",
                  cursor="hand2", command=self._remove_staff).pack(side="left", padx=4)
        tk.Button(tb, text="🔄 Refresh", font=FONT_BUTTON,
                  bg=PALETTE["accent2"], fg="white", relief="flat",
                  cursor="hand2", command=self._load_staff).pack(side="right")

        cols = ("ID", "Username", "Email", "Role")
        self._staff_tree = self._make_tree(parent, cols)
        self._load_staff()

    def _load_staff(self):
        tree = self._staff_tree
        tree.delete(*tree.get_children())
        for u in self._ctrl.manage_staff("list"):
            tree.insert("", "end", iid=u["userId"],
                        values=(u["userId"], u["username"], u["email"], u["role"]))

    def _add_staff_dialog(self):
        _FormDialog(self, title="Add Staff Member",
                    fields=[
                        ("Username", "username"),
                        ("Password", "password"),
                        ("Email",    "email"),
                        ("Role (BookingStaff/Admin/Manager)", "role"),
                    ],
                    on_submit=lambda v: self._ctrl.manage_staff("add", **v),
                    on_success=self._load_staff)

    def _remove_staff(self):
        sel = self._staff_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Please select a staff member.")
            return
        uid = int(sel[0])
        if messagebox.askyesno("Remove", f"Remove user ID {uid}?"):
            try:
                self._ctrl.manage_staff("remove", user_id=uid)
                self._load_staff()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    # ═══════════════════════════════════════════════════════════════════════════
    # PRICING TAB
    # ═══════════════════════════════════════════════════════════════════════════

    def _build_pricing_tab(self):
        parent = self._tab_pricing

        tb = tk.Frame(parent, bg=PALETTE["bg"])
        tb.pack(fill="x", pady=(8, 4), padx=8)
        tk.Button(tb, text="✏️ Update Selected Price", font=FONT_BUTTON,
                  bg=PALETTE["accent2"], fg="white", relief="flat",
                  cursor="hand2", command=self._update_price_dialog).pack(side="left")
        tk.Button(tb, text="🔄 Refresh", font=FONT_BUTTON,
                  bg=PALETTE["accent2"], fg="white", relief="flat",
                  cursor="hand2", command=self._load_pricing).pack(side="right")

        cols = ("City", "Show Type", "Base Price", "Upper Gallery", "VIP")
        self._price_tree = self._make_tree(parent, cols)
        self._load_pricing()

    def _load_pricing(self):
        tree = self._price_tree
        tree.delete(*tree.get_children())
        from models.pricing_rule import PricingRule
        for rule in PricingRule.get_all():
            tree.insert("", "end",
                        iid=f"{rule.city}|{rule.showType}",
                        values=(rule.city, rule.showType,
                                f"£{rule.basePrice:.2f}",
                                f"£{rule.calcUpper():.2f}",
                                f"£{rule.calcVIP():.2f}"))

    def _update_price_dialog(self):
        sel = self._price_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a pricing rule first.")
            return
        city, show_type = sel[0].split("|")
        _FormDialog(self, title=f"Update Price: {city} / {show_type}",
                    fields=[("New Base Price (£)", "base_price")],
                    on_submit=lambda v: self._ctrl.update_pricing(
                        city, show_type, float(v["base_price"])
                    ),
                    on_success=self._load_pricing)

    # ═══════════════════════════════════════════════════════════════════════════
    # REPORTS TAB (inherits from AdminController)
    # ═══════════════════════════════════════════════════════════════════════════

    def _build_reports_tab(self):
        parent = self._tab_reports

        ctrl_frame = tk.Frame(parent, bg=PALETTE["bg"])
        ctrl_frame.pack(fill="x", padx=8, pady=12)
        tk.Label(ctrl_frame, text="Report Type:", font=FONT_LABEL,
                 bg=PALETTE["bg"], fg=PALETTE["muted"]).pack(side="left")
        self._report_var = tk.StringVar(value="bookings")
        for rt in ["bookings", "revenue", "cancellations", "occupancy"]:
            ttk.Radiobutton(ctrl_frame, text=rt.capitalize(),
                            variable=self._report_var, value=rt).pack(side="left", padx=8)

        tk.Button(ctrl_frame, text="▶ Generate", font=FONT_BUTTON,
                  bg=PALETTE["success"], fg="white", relief="flat",
                  cursor="hand2", command=self._generate_report).pack(side="left", padx=16)

        self._report_tree = ttk.Treeview(parent, show="headings")
        vsb = ttk.Scrollbar(parent, orient="vertical",   command=self._report_tree.yview)
        hsb = ttk.Scrollbar(parent, orient="horizontal", command=self._report_tree.xview)
        self._report_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        hsb.pack(side="bottom", fill="x", padx=8)
        vsb.pack(side="right",  fill="y")
        self._report_tree.pack(fill="both", expand=True, padx=(8, 0), pady=4)

    def _generate_report(self):
        rtype  = self._report_var.get()
        report = self._admin.generate_report(rtype)
        tree   = self._report_tree

        if not report.data:
            messagebox.showinfo("Empty", "No data for this report.")
            return

        cols = list(report.data[0].keys())
        tree["columns"] = cols
        for col in cols:
            tree.heading(col, text=col.replace("_", " ").title())
            tree.column(col, width=130, minwidth=80)
        tree.delete(*tree.get_children())
        for row in report.data:
            tree.insert("", "end", values=list(row.values()))

    # ── Helper ─────────────────────────────────────────────────────────────────

    def _make_tree(self, parent, cols):
        frame = tk.Frame(parent, bg=PALETTE["bg"])
        frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        tree = ttk.Treeview(frame, columns=cols, show="headings")
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=140, minwidth=80)
        vsb = ttk.Scrollbar(frame, orient="vertical",   command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        hsb.pack(side="bottom", fill="x")
        vsb.pack(side="right",  fill="y")
        tree.pack(fill="both", expand=True)
        return tree


# ── Generic form dialog ───────────────────────────────────────────────────────

class _FormDialog(tk.Toplevel):
    """A reusable labelled-entry form dialog."""

    def __init__(self, master, title: str, fields: list,
                 on_submit, on_success=None):
        super().__init__(master)
        self._fields     = fields
        self._on_submit  = on_submit
        self._on_success = on_success
        self.title(title)
        self.geometry("400x" + str(100 + len(fields) * 48))
        self.resizable(False, False)
        self.configure(bg=PALETTE["bg"])
        self._build()

    def _build(self):
        inner = tk.Frame(self, bg=PALETTE["bg"])
        inner.pack(padx=24, pady=20, fill="both", expand=True)

        self._vars = {}
        for i, (label, key) in enumerate(self._fields):
            tk.Label(inner, text=label, font=FONT_LABEL,
                     bg=PALETTE["bg"], fg=PALETTE["muted"]).grid(
                row=i, column=0, sticky="w", pady=6)
            var = tk.StringVar()
            self._vars[key] = var
            show = "●" if key == "password" else ""
            ttk.Entry(inner, textvariable=var, show=show,
                      font=FONT_INPUT, width=28).grid(
                row=i, column=1, padx=(12, 0), pady=6, sticky="ew")

        self._status = tk.Label(inner, text="", font=FONT_LABEL,
                                bg=PALETTE["bg"], fg=PALETTE["accent"],
                                wraplength=360)
        self._status.grid(row=len(self._fields), column=0, columnspan=2, pady=(6, 0))

        tk.Button(inner, text="Save",
                  font=FONT_BUTTON, bg=PALETTE["success"],
                  fg="white", relief="flat", cursor="hand2",
                  command=self._save).grid(
            row=len(self._fields)+1, column=0, columnspan=2,
            sticky="ew", pady=(10, 0), ipady=6)

    def _save(self):
        values = {k: v.get() for k, v in self._vars.items()}
        try:
            self._on_submit(values)
            if self._on_success:
                self._on_success()
            self.destroy()
        except Exception as e:
            self._status.config(text=str(e))
