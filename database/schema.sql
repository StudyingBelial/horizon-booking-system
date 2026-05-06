-- schema.sql
-- Horizon Cinemas Booking System — SQLite Schema
-- Run via db_manager.py on first startup

PRAGMA foreign_keys = ON;

-- ─── Users ───────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    userId       INTEGER PRIMARY KEY AUTOINCREMENT,
    username     TEXT    NOT NULL UNIQUE,
    passwordHash TEXT    NOT NULL,
    email        TEXT    NOT NULL,
    role         TEXT    NOT NULL CHECK(role IN ('BookingStaff','Admin','Manager'))
);

-- ─── Cinemas ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS cinemas (
    cinemaId INTEGER PRIMARY KEY AUTOINCREMENT,
    name     TEXT    NOT NULL,
    city     TEXT    NOT NULL,
    address  TEXT    NOT NULL
);

-- ─── Screens ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS screens (
    screenId          INTEGER PRIMARY KEY AUTOINCREMENT,
    cinemaId          INTEGER NOT NULL REFERENCES cinemas(cinemaId),
    screenNumber      INTEGER NOT NULL,
    totalCapacity     INTEGER NOT NULL,
    lowerHallSeats    INTEGER NOT NULL,
    upperGallerySeats INTEGER NOT NULL
);

-- ─── Films ───────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS films (
    filmId      INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT    NOT NULL,
    description TEXT,
    genre       TEXT,
    ageRating   TEXT,
    actors      TEXT
);

-- ─── Listings ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS listings (
    listingId INTEGER PRIMARY KEY AUTOINCREMENT,
    filmId    INTEGER NOT NULL REFERENCES films(filmId),
    screenId  INTEGER NOT NULL REFERENCES screens(screenId),
    showDate  TEXT    NOT NULL,   -- YYYY-MM-DD
    showTime  TEXT    NOT NULL,   -- HH:MM
    showType  TEXT    NOT NULL CHECK(showType IN ('Standard','IMAX','3D','Directors'))
);

-- ─── Seats ───────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS seats (
    seatId     INTEGER PRIMARY KEY AUTOINCREMENT,
    screenId   INTEGER NOT NULL REFERENCES screens(screenId),
    seatNumber TEXT    NOT NULL,  -- e.g. A1, B3, VIP-01
    seatType   TEXT    NOT NULL CHECK(seatType IN ('Lower','Upper','VIP'))
);

-- ─── Pricing Rules ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS pricing_rules (
    ruleId    INTEGER PRIMARY KEY AUTOINCREMENT,
    city      TEXT    NOT NULL,
    showType  TEXT    NOT NULL CHECK(showType IN ('Standard','IMAX','3D','Directors')),
    timeSlot  TEXT    NOT NULL CHECK(timeSlot IN ('Morning','Afternoon','Evening')),
    basePrice REAL    NOT NULL,
    UNIQUE(city, showType, timeSlot)
);

-- ─── Bookings ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS bookings (
    bookingId   INTEGER PRIMARY KEY AUTOINCREMENT,
    bookingRef  TEXT    NOT NULL UNIQUE,
    listingId   INTEGER NOT NULL REFERENCES listings(listingId),
    staffId     INTEGER NOT NULL REFERENCES users(userId),
    bookingDate TEXT    NOT NULL,  -- YYYY-MM-DD HH:MM:SS
    numTickets  INTEGER NOT NULL,
    totalCost   REAL    NOT NULL,
    status      TEXT    NOT NULL DEFAULT 'Confirmed'
                        CHECK(status IN ('Confirmed','Cancelled'))
);

-- ─── Booked Seats ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS booked_seats (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    bookingId    INTEGER NOT NULL REFERENCES bookings(bookingId),
    seatId       INTEGER NOT NULL REFERENCES seats(seatId),
    ticketType   TEXT    NOT NULL CHECK(ticketType IN ('Lower','Upper','VIP')),
    priceCharged REAL    NOT NULL
);

-- ─── Cancellations ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS cancellations (
    cancellationId INTEGER PRIMARY KEY AUTOINCREMENT,
    bookingRef     TEXT    NOT NULL UNIQUE REFERENCES bookings(bookingRef),
    cancelDate     TEXT    NOT NULL,   -- YYYY-MM-DD HH:MM:SS
    refundAmount   REAL    NOT NULL,
    chargeRate     REAL    NOT NULL DEFAULT 0.5
);

-- ─── Indexes ─────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_listings_date     ON listings(showDate);
CREATE INDEX IF NOT EXISTS idx_listings_screen   ON listings(screenId);
CREATE INDEX IF NOT EXISTS idx_bookings_ref      ON bookings(bookingRef);
CREATE INDEX IF NOT EXISTS idx_bookings_listing  ON bookings(listingId);
CREATE INDEX IF NOT EXISTS idx_booked_seats_bk   ON booked_seats(bookingId);
CREATE INDEX IF NOT EXISTS idx_booked_seats_seat ON booked_seats(seatId);
CREATE INDEX IF NOT EXISTS idx_seats_screen      ON seats(screenId);
