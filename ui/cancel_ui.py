# Author: StudyingBelial | Student ID: 1234567
# Module: UFCF8S-30-2 Advanced Software Development

"""
ui/cancel_ui.py — Booking cancellation interface.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from controllers.booking_controller import BookingController
from ui.login_ui import PALETTE, FONT_TITLE, FONT_LABEL, FONT_BUTTON, FONT_INPUT
from models.cancellation import Cancellation


class CancelUI(tk.Toplevel):

    def __init__(self, master):
        super().__init__(master)
        self.title("Horizon Cinemas — Cancel Booking")
        self.geometry("520x480")
        self.resizable(False, False)
        self.configure(bg=PALETTE["bg"])
        self._ctrl = BookingController()
        self._build()

    def _build(self):
        # Header
        bar = tk.Frame(self, bg=PALETTE["accent"], pady=8)
        bar.pack(fill="x")
        tk.Label(
            bar,
            text="❌  Cancel a Booking",
            font=("Helvetica", 13, "bold"),
            bg=PALETTE["accent"],
            fg="white",
        ).pack(padx=16, anchor="w")

        # Card
        card = tk.Frame(
            self,
            bg=PALETTE["surface"],
            highlightthickness=1,
            highlightbackground=PALETTE["border"],
        )
        card.pack(padx=32, pady=24, fill="x")
        inner = tk.Frame(card, bg=PALETTE["surface"])
        inner.pack(padx=24, pady=24, fill="x")

        tk.Label(
            inner,
            text="Enter Booking Reference",
            font=FONT_TITLE,
            bg=PALETTE["surface"],
            fg=PALETTE["text"],
        ).pack(anchor="w")
        tk.Label(
            inner,
            text="e.g. HCB-A1B2C3D4",
            font=FONT_LABEL,
            bg=PALETTE["surface"],
            fg=PALETTE["muted"],
        ).pack(anchor="w", pady=(2, 16))

        ref_frame = tk.Frame(inner, bg=PALETTE["surface"])
        ref_frame.pack(fill="x")
        self._ref_var = tk.StringVar()
        entry = ttk.Entry(ref_frame, textvariable=self._ref_var, font=FONT_INPUT)
        entry.pack(side="left", fill="x", expand=True, ipady=6)
        entry.bind("<Return>", lambda e: self._lookup())
        self._inner_card = inner
        self._btn(ref_frame, "Look Up", self._lookup, bg=PALETTE["accent2"])

        # Info frame (shown after lookup)
        self._info_frame = tk.Frame(inner, bg=PALETTE["surface"])
        self._info_frame.pack(fill="x", pady=(16, 0))

        # Confirm cancellation button (hidden until eligible booking is found)
        self._cancel_btn_f = tk.Button(
            inner,
            text="✅  Confirm Cancellation",
            command=self._confirm_cancel,
            font=FONT_BUTTON,
            bg=PALETTE["accent"],
            fg="white",
            cursor="hand2",
            relief="flat",
            activebackground=PALETTE["accent2"],
            activeforeground="white",
            padx=8,
            pady=8,
        )
        # Not packed yet — shown only when booking is eligible

        # Status / result label
        self._status = tk.Label(
            inner,
            text="",
            font=FONT_LABEL,
            bg=PALETTE["surface"],
            fg=PALETTE["muted"],
            wraplength=440,
            justify="left",
        )
        self._status.pack(anchor="w", pady=(12, 0))

    def _btn(self, parent, text, command, bg=None, side="left", padx=4):
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

    def _lookup(self):
        # Clear previous results
        for w in self._info_frame.winfo_children():
            w.destroy()
        self._cancel_btn_f.pack_forget()
        self._status.config(text="")

        ref = self._ref_var.get().strip().upper()
        if not ref:
            self._status.config(
                text="Please enter a booking reference.", fg=PALETTE["accent"]
            )
            return

        booking = self._ctrl.lookup_booking(ref)
        if not booking:
            self._status.config(
                text=f"No booking found for reference: {ref}", fg=PALETTE["accent"]
            )
            return

        self._booking = booking

        # Display booking details
        listing = booking.getListing()
        film = listing.getFilm() if listing else None

        rows = [
            ("Booking Ref", booking.bookingRef),
            ("Film", film.title if film else "N/A"),
            ("Date", listing.showDate if listing else "N/A"),
            ("Time", listing.showTime if listing else "N/A"),
            ("Show Type", listing.showType if listing else "N/A"),
            ("Tickets", str(booking.numTickets)),
            ("Total Cost", f"£{booking.totalCost:.2f}"),
            ("Status", booking.status),
        ]

        for i, (label, value) in enumerate(rows):
            tk.Label(
                self._info_frame,
                text=f"{label}:",
                font=("Helvetica", 9, "bold"),
                bg=PALETTE["surface"],
                fg=PALETTE["muted"],
                anchor="w",
            ).grid(row=i, column=0, sticky="w", pady=1)
            tk.Label(
                self._info_frame,
                text=value,
                font=("Helvetica", 9),
                bg=PALETTE["surface"],
                fg=PALETTE["success"] if (label == "Status" and value == "Confirmed")
                   else PALETTE["accent"] if label == "Status"
                   else PALETTE["text"],
                anchor="w",
            ).grid(row=i, column=1, sticky="w", padx=(16, 0), pady=1)

        # Check eligibility
        eligible = booking.isEligibleCancel()
        refund = Cancellation.calcRefundStatic(booking.totalCost)

        if eligible:
            self._status.config(
                text=f"✅ Eligible for cancellation. Refund: £{refund:.2f}",
                fg=PALETTE["success"],
            )
            self._cancel_btn_f.pack(fill="x", pady=(12, 0))
        else:
            if booking.status == "Cancelled":
                msg = "⚠️ This booking has already been cancelled."
            else:
                msg = (
                    "❌ Not eligible: cancellations are only allowed "
                    "more than 1 day before the show date."
                )
            self._status.config(text=msg, fg=PALETTE["warning"])

    def _confirm_cancel(self):
        ref = self._booking.bookingRef
        confirm = messagebox.askyesno(
            "Confirm Cancellation",
            f"Cancel booking {ref}?\n\n"
            f"Refund: £{Cancellation.calcRefundStatic(self._booking.totalCost):.2f}\n\n"
            f"This action cannot be undone.",
        )
        if not confirm:
            return
        try:
            result = self._ctrl.cancel_booking(ref)
            messagebox.showinfo("Cancelled", result["message"])
            self._cancel_btn_f.pack_forget()
            self._status.config(
                text=f"✅ Cancellation processed. Refund: £{result['refund']:.2f}",
                fg=PALETTE["success"],
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))