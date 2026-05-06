"""
ui/booking_ui.py — Full booking interface for BookingStaff (and Admin/Manager).

Workflow:
  1. Select a listing (film / cinema / date)
  2. Browse available seats (colour-coded grid)
  3. Review price breakdown
  4. Confirm booking → receipt popup
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from controllers.booking_controller import BookingController
from controllers.auth_controller    import AuthController
from models.listing import Listing
from models.film    import Film
from models.cinema  import Cinema
from models.screen  import Screen
from ui.login_ui    import PALETTE, FONT_TITLE, FONT_SUB, FONT_LABEL, FONT_BUTTON, FONT_INPUT
from database.db_manager import db


class BookingUI(tk.Toplevel):

    def __init__(self, master, user):
        super().__init__(master)
        self.user       = user
        self._ctrl      = BookingController()
        self._selected  = []          # list of selected seat IDs
        self._listing   = None        # currently chosen Listing
        self._seat_btns = {}          # seatId → tk.Button

        self.title(f"Horizon Cinemas — Booking [{user.username}]")
        self.geometry("1050x720")
        self.configure(bg=PALETTE["bg"])
        self._build()
        self._load_films()

    # ── Layout construction ───────────────────────────────────────────────────

    def _build(self):
        # Top bar
        bar = tk.Frame(self, bg=PALETTE["accent2"], pady=8)
        bar.pack(fill="x")
        tk.Label(bar, text="🎬  Horizon Cinemas — New Booking",
                 font=("Helvetica", 13, "bold"),
                 bg=PALETTE["accent2"], fg="white").pack(side="left", padx=16)
        tk.Label(bar, text=f"Logged in as: {self.user.username}  [{self.user.role}]",
                 font=FONT_LABEL,
                 bg=PALETTE["accent2"], fg="#AACCFF").pack(side="right", padx=(16, 8))

        # Custom Logout button
        log_f = tk.Frame(bar, bg="#E94560", padx=0, pady=0)
        log_f.pack(side="right", padx=16)
        log_l = tk.Label(log_f, text="Logout 🚪", font=("Helvetica", 9, "bold"),
                         bg="#E94560", fg="white", padx=12, pady=4,
                         cursor="hand2")
        log_l.pack()
        log_l.bind("<Enter>", lambda e: log_l.config(bg="#C0392B"))
        log_l.bind("<Leave>", lambda e: log_l.config(bg="#E94560"))
        log_l.bind("<Button-1>", lambda e: self.master.show_login(self))

        # ── Main paned layout ────────────────────────────────────────────────
        paned = tk.PanedWindow(self, orient="horizontal",
                               bg=PALETTE["bg"], sashwidth=4,
                               sashrelief="flat")
        paned.pack(fill="both", expand=True, padx=10, pady=10)

        left  = tk.Frame(paned, bg=PALETTE["bg"])
        right = tk.Frame(paned, bg=PALETTE["bg"])
        paned.add(left,  minsize=360)
        paned.add(right, minsize=460)

        self._build_selection_panel(left)
        self._build_seat_panel(right)

    def _btn(self, parent, text, command, bg=None, side="top", pady=2):
        """Helper to create custom Frame+Label buttons for macOS consistency."""
        color = bg if bg else PALETTE["accent"]
        f = tk.Frame(parent, bg=color, padx=0, pady=0)
        f.pack(side=side, fill="x", pady=pady)
        l = tk.Label(f, text=text, font=FONT_BUTTON,
                     bg=color, fg="white", padx=12, pady=10,
                     cursor="hand2")
        l.pack(fill="x")
        l.bind("<Enter>", lambda e: l.config(bg=PALETTE["accent2"]))
        l.bind("<Leave>", lambda e: l.config(bg=color))
        l.bind("<Button-1>", lambda e: command())
        return f

    def _build_selection_panel(self, parent):
        """Left panel: film, cinema, listing selection + price info."""
        def section(text):
            f = tk.Frame(parent, bg=PALETTE["surface"],
                         highlightthickness=1,
                         highlightbackground=PALETTE["border"])
            f.pack(fill="x", pady=(0, 8))
            tk.Label(f, text=text, font=("Helvetica", 10, "bold"),
                     bg=PALETTE["accent2"], fg="white",
                     anchor="w", padx=10, pady=4).pack(fill="x")
            inner = tk.Frame(f, bg=PALETTE["surface"])
            inner.pack(fill="x", padx=10, pady=8)
            return inner

        # ── Film picker ───────────────────────────────────────────────────────
        f1 = section("① Select Film")
        tk.Label(f1, text="Film:", font=FONT_LABEL,
                 bg=PALETTE["surface"], fg=PALETTE["muted"]).grid(row=0, column=0, sticky="w")
        self._film_var = tk.StringVar()
        self._film_cb  = ttk.Combobox(f1, textvariable=self._film_var,
                                      state="readonly", font=FONT_INPUT, width=34)
        self._film_cb.grid(row=0, column=1, padx=(8, 0), sticky="ew")
        self._film_cb.bind("<<ComboboxSelected>>", self._on_film_select)

        # ── Cinema picker ─────────────────────────────────────────────────────
        f2 = section("② Select Cinema & Listing")
        tk.Label(f2, text="Cinema:", font=FONT_LABEL,
                 bg=PALETTE["surface"], fg=PALETTE["muted"]).grid(row=0, column=0, sticky="w")
        self._cinema_var = tk.StringVar()
        self._cinema_cb  = ttk.Combobox(f2, textvariable=self._cinema_var,
                                        state="readonly", font=FONT_INPUT, width=34)
        self._cinema_cb.grid(row=0, column=1, padx=(8, 0), sticky="ew")
        self._cinema_cb.bind("<<ComboboxSelected>>", self._on_cinema_select)

        tk.Label(f2, text="Showing:", font=FONT_LABEL,
                 bg=PALETTE["surface"], fg=PALETTE["muted"]).grid(row=1, column=0, sticky="w", pady=(6, 0))
        self._listing_var = tk.StringVar()
        self._listing_cb  = ttk.Combobox(f2, textvariable=self._listing_var,
                                         state="readonly", font=FONT_INPUT, width=34)
        self._listing_cb.grid(row=1, column=1, padx=(8, 0), pady=(6, 0), sticky="ew")
        self._listing_cb.bind("<<ComboboxSelected>>", self._on_listing_select)

        # ── Price breakdown ───────────────────────────────────────────────────
        f3 = section("③ Ticket Prices")
        for i, (label, attr) in enumerate([
            ("Lower Hall:", "_price_lower"),
            ("Upper Gallery:", "_price_upper"),
            ("VIP:", "_price_vip"),
        ]):
            tk.Label(f3, text=label, font=FONT_LABEL,
                     bg=PALETTE["surface"], fg=PALETTE["muted"]).grid(
                row=i, column=0, sticky="w", pady=2)
            lbl = tk.Label(f3, text="—", font=("Helvetica", 10, "bold"),
                           bg=PALETTE["surface"], fg=PALETTE["text"])
            lbl.grid(row=i, column=1, sticky="w", padx=(12, 0))
            setattr(self, attr, lbl)

        # ── Booking summary ───────────────────────────────────────────────────
        f4 = section("④ Booking Summary")
        tk.Label(f4, text="Selected seats:", font=FONT_LABEL,
                 bg=PALETTE["surface"], fg=PALETTE["muted"]).grid(row=0, column=0, sticky="w")
        self._sel_label = tk.Label(f4, text="None", font=FONT_LABEL,
                                   bg=PALETTE["surface"], fg=PALETTE["text"],
                                   wraplength=200, anchor="w", justify="left")
        self._sel_label.grid(row=0, column=1, sticky="w", padx=(8, 0))

        tk.Label(f4, text="Total cost:", font=FONT_LABEL,
                 bg=PALETTE["surface"], fg=PALETTE["muted"]).grid(row=1, column=0, sticky="w", pady=(6, 0))
        self._total_label = tk.Label(f4, text="£0.00",
                                     font=("Helvetica", 14, "bold"),
                                     bg=PALETTE["surface"], fg=PALETTE["success"])
        self._total_label.grid(row=1, column=1, sticky="w", padx=(8, 0), pady=(6, 0))

        # ── Action buttons ────────────────────────────────────────────────────
        btn_frame = tk.Frame(parent, bg=PALETTE["bg"])
        btn_frame.pack(fill="x", pady=(4, 0))

        self._btn(btn_frame, "✅  Confirm Booking", self._confirm_booking, bg=PALETTE["success"])
        self._btn(btn_frame, "❌  Cancel Booking", self._open_cancel, bg=PALETTE["accent"])

    def _build_seat_panel(self, parent):
        """Right panel: seat grid visualisation."""
        tk.Label(parent, text="Seat Map",
                 font=("Helvetica", 12, "bold"),
                 bg=PALETTE["bg"], fg=PALETTE["text"]).pack(anchor="w", pady=(0, 4))

        # Legend
        legend = tk.Frame(parent, bg=PALETTE["bg"])
        legend.pack(anchor="w", pady=(0, 8))
        for color, label in [
            ("#2C5F8A", "Lower Hall"),
            ("#5A3E7A", "Upper Gallery"),
            ("#8A5A00", "VIP"),
            ("#3A6B3A", "Selected"),
            ("#5A5A5A", "Booked"),
        ]:
            sq = tk.Frame(legend, bg=color, width=14, height=14)
            sq.pack(side="left")
            tk.Label(legend, text=f" {label}  ", font=("Helvetica", 8),
                     bg=PALETTE["bg"], fg=PALETTE["muted"]).pack(side="left")

        # Scrollable seat canvas
        canvas_frame = tk.Frame(parent, bg=PALETTE["surface"],
                                highlightthickness=1,
                                highlightbackground=PALETTE["border"])
        canvas_frame.pack(fill="both", expand=True)

        self._seat_canvas = tk.Canvas(canvas_frame,
                                      bg=PALETTE["surface"],
                                      highlightthickness=0)
        vsb = ttk.Scrollbar(canvas_frame, orient="vertical",
                             command=self._seat_canvas.yview)
        self._seat_canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self._seat_canvas.pack(fill="both", expand=True)

        self._seat_inner = tk.Frame(self._seat_canvas, bg=PALETTE["surface"])
        self._seat_canvas_window = self._seat_canvas.create_window(
            (0, 0), window=self._seat_inner, anchor="nw"
        )
        self._seat_inner.bind("<Configure>", lambda e: self._seat_canvas.configure(
            scrollregion=self._seat_canvas.bbox("all")
        ))

        # Placeholder label
        self._seat_placeholder = tk.Label(
            self._seat_inner,
            text="← Select a showing to view seats",
            font=FONT_SUB, bg=PALETTE["surface"], fg=PALETTE["muted"],
        )
        self._seat_placeholder.pack(padx=20, pady=40)

    # ── Data loading ──────────────────────────────────────────────────────────

    def _load_films(self):
        self._films = Film.get_all()
        self._film_cb["values"] = [f.title for f in self._films]
        self._film_map  = {f.title: f for f in self._films}

    def _on_film_select(self, _=None):
        film = self._film_map.get(self._film_var.get())
        if not film:
            return
        self._selected_film = film
        # Load cinemas that have this film listed
        rows = db.fetchall(
            """
            SELECT DISTINCT c.cinemaId, c.name, c.city
            FROM listings l
            JOIN screens s ON l.screenId = s.screenId
            JOIN cinemas c ON s.cinemaId = c.cinemaId
            WHERE l.filmId = ? AND l.showDate >= DATE('now')
            ORDER BY c.city, c.name
            """,
            (film.filmId,),
        )
        self._cinemas_for_film = {f"{r['city']} — {r['name']}": r["cinemaId"]
                                  for r in rows}
        self._cinema_cb["values"] = list(self._cinemas_for_film.keys())
        self._cinema_var.set("")
        self._listing_var.set("")
        self._clear_seat_grid()

    def _on_cinema_select(self, _=None):
        cinema_key = self._cinema_var.get()
        cinema_id  = self._cinemas_for_film.get(cinema_key)
        film       = getattr(self, "_selected_film", None)
        if not cinema_id or not film:
            return
        rows = db.fetchall(
            """
            SELECT l.listingId, l.showDate, l.showTime, l.showType,
                   s.screenNumber
            FROM listings l
            JOIN screens s ON l.screenId = s.screenId
            WHERE l.filmId=? AND s.cinemaId=? AND l.showDate >= DATE('now')
            ORDER BY l.showDate, l.showTime
            """,
            (film.filmId, cinema_id),
        )
        self._listings_for_sel = {}
        labels = []
        for r in rows:
            key = (f"{r['showDate']}  {r['showTime']}  "
                   f"[{r['showType']}]  Screen {r['screenNumber']}")
            self._listings_for_sel[key] = r["listingId"]
            labels.append(key)
        self._listing_cb["values"] = labels
        self._listing_var.set("")
        self._clear_seat_grid()

    def _on_listing_select(self, _=None):
        key        = self._listing_var.get()
        listing_id = self._listings_for_sel.get(key)
        if not listing_id:
            return
        self._listing   = Listing.get_by_id(listing_id)
        self._selected  = []
        self._update_price_display()
        self._render_seat_grid()

    # ── Seat grid ─────────────────────────────────────────────────────────────

    def _clear_seat_grid(self):
        for w in self._seat_inner.winfo_children():
            w.destroy()
        self._seat_placeholder = tk.Label(
            self._seat_inner,
            text="← Select a showing to view seats",
            font=FONT_SUB, bg=PALETTE["surface"], fg=PALETTE["muted"],
        )
        self._seat_placeholder.pack(padx=20, pady=40)
        self._seat_btns = {}
        self._selected  = []
        self._update_summary()

    def _render_seat_grid(self):
        for w in self._seat_inner.winfo_children():
            w.destroy()
        self._seat_btns = {}

        avail_ids  = {s.seatId for s in self._listing.getAvailableSeats()}
        all_seats  = __import__("models.seat", fromlist=["Seat"]).Seat.get_by_screen(
            self._listing.screenId
        )

        type_colors = {
            "Lower": "#2C5F8A",
            "Upper": "#5A3E7A",
            "VIP":   "#8A5A00",
        }

        # Group by type
        from collections import defaultdict
        groups = defaultdict(list)
        for seat in all_seats:
            groups[seat.seatType].append(seat)

        for seat_type in ["Lower", "Upper", "VIP"]:
            seats = groups[seat_type]
            if not seats:
                continue

            # Section header
            tk.Label(self._seat_inner,
                     text=f"── {seat_type} Hall ──",
                     font=("Helvetica", 9, "bold"),
                     bg=PALETTE["surface"], fg=PALETTE["muted"]).pack(
                anchor="w", padx=8, pady=(10, 4))

            # Seat buttons in rows of 10
            row_frame = None
            base_color = type_colors[seat_type]

            for idx, seat in enumerate(seats):
                if idx % 10 == 0:
                    row_frame = tk.Frame(self._seat_inner, bg=PALETTE["surface"])
                    row_frame.pack(anchor="w", padx=8, pady=1)

                available = seat.seatId in avail_ids
                bg = base_color if available else "#5A5A5A"
                
                # Using a Label instead of Button for consistent macOS visibility
                btn = tk.Label(
                    row_frame,
                    text=seat.seatNumber,
                    font=("Helvetica", 7, "bold"),
                    bg=bg, fg="white",
                    width=5, height=1,
                    cursor="hand2" if available else "arrow"
                )
                btn.pack(side="left", padx=1, pady=1)
                
                if available:
                    btn.bind("<Button-1>", lambda e, s=seat: self._toggle_seat(s))
                    self._seat_btns[seat.seatId] = (btn, seat, base_color)
                else:
                    btn.config(fg="#888888") # Muted text for booked seats

        # Screen label at bottom
        tk.Label(self._seat_inner,
                 text="▬▬▬▬▬▬▬  SCREEN  ▬▬▬▬▬▬▬",
                 font=("Helvetica", 9), bg=PALETTE["surface"],
                 fg=PALETTE["muted"]).pack(pady=(16, 8))

    def _toggle_seat(self, seat):
        if seat.seatId in self._selected:
            self._selected.remove(seat.seatId)
            lbl, _, orig_color = self._seat_btns[seat.seatId]
            lbl.configure(bg=orig_color, fg="white")
        else:
            self._selected.append(seat.seatId)
            lbl, _, _ = self._seat_btns[seat.seatId]
            lbl.configure(bg="#3A6B3A", fg="white")
        self._update_summary()

    # ── Price / summary updates ───────────────────────────────────────────────

    def _update_price_display(self):
        if not self._listing:
            return
        prices = self._ctrl.get_price_breakdown(self._listing.listingId)
        self._price_lower.config(text=f"£{prices.get('Lower', 0):.2f}")
        self._price_upper.config(text=f"£{prices.get('Upper', 0):.2f}")
        self._price_vip.config(  text=f"£{prices.get('VIP',   0):.2f}")

    def _update_summary(self):
        if not self._selected:
            self._sel_label.config(text="None")
            self._total_label.config(text="£0.00")
            return

        from models.seat import Seat
        seat_strs = []
        total = 0.0
        for sid in self._selected:
            seat = Seat.get_by_id(sid)
            price = self._ctrl._pricing.get_seat_price(
                self._listing.listingId, sid
            ) if self._listing else 0
            seat_strs.append(f"{seat.seatNumber} ({seat.seatType})")
            total += price

        self._sel_label.config(text=", ".join(seat_strs))
        self._total_label.config(text=f"£{total:.2f}")

    # ── Booking confirmation ──────────────────────────────────────────────────

    def _confirm_booking(self):
        if not self._listing:
            messagebox.showwarning("No Listing", "Please select a showing first.")
            return
        if not self._selected:
            messagebox.showwarning("No Seats", "Please select at least one seat.")
            return

        try:
            result = self._ctrl.create_booking(
                listing_id = self._listing.listingId,
                seat_ids   = self._selected,
                staff_id   = self.user.userId,
            )
            self._show_receipt(result["receipt"], result["booking"].bookingRef)
            # Reset UI
            self._selected = []
            self._render_seat_grid()
            self._update_summary()
        except Exception as e:
            messagebox.showerror("Booking Failed", str(e))

    def _show_receipt(self, receipt_text: str, booking_ref: str):
        win = tk.Toplevel(self)
        win.title(f"Receipt — {booking_ref}")
        win.geometry("480x500")
        win.configure(bg=PALETTE["bg"])

        tk.Label(win, text="Booking Confirmed! ✅",
                 font=("Helvetica", 14, "bold"),
                 bg=PALETTE["bg"], fg=PALETTE["success"]).pack(pady=(16, 4))

        txt = scrolledtext.ScrolledText(win, font=("Courier", 10),
                                        bg=PALETTE["surface"],
                                        fg=PALETTE["text"],
                                        relief="flat", wrap="word",
                                        height=20)
        txt.pack(padx=16, pady=8, fill="both", expand=True)
        txt.insert("1.0", receipt_text)
        txt.configure(state="disabled")

        tk.Button(win, text="Close", font=FONT_BUTTON,
                  bg=PALETTE["accent2"], fg="white", relief="flat",
                  cursor="hand2", command=win.destroy).pack(pady=(4, 16))

    def _open_cancel(self):
        from ui.cancel_ui import CancelUI
        CancelUI(self)
