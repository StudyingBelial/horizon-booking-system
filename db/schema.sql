-- Users & Roles
CREATE TABLE users (
  user_id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  role TEXT CHECK(role IN ('staff', 'admin', 'manager')) NOT NULL,
  is_active INTEGER DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE admins (
  admin_id INTEGER PRIMARY KEY,
  FOREIGN KEY (admin_id) REFERENCES users(user_id)
);

CREATE TABLE managers (
  manager_id INTEGER PRIMARY KEY,
  FOREIGN KEY (manager_id) REFERENCES users(user_id)
);

-- Cinema Structure
-- NOTE: cities and cinemas are defined before booking_staff so the FK
-- reference to cinemas(cinema_id) is valid on all database engines.
CREATE TABLE cities (
  city_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL
);

CREATE TABLE cinemas (
  cinema_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  city_id INTEGER NOT NULL,
  address TEXT NOT NULL,
  FOREIGN KEY (city_id) REFERENCES cities(city_id)
);

CREATE TABLE booking_staff (
  staff_id INTEGER PRIMARY KEY,
  cinema_id INTEGER NOT NULL,
  FOREIGN KEY (staff_id) REFERENCES users(user_id),
  FOREIGN KEY (cinema_id) REFERENCES cinemas(cinema_id)
);

-- Screens
-- NOTE: lower_hall_seats should be approximately 30% of total_capacity.
-- This is enforced at the application layer, not via a CHECK constraint,
-- to allow minor rounding flexibility across different screen sizes.
CREATE TABLE screens (
  screen_id INTEGER PRIMARY KEY AUTOINCREMENT,
  cinema_id INTEGER NOT NULL,
  screen_number INTEGER NOT NULL,
  total_capacity INTEGER NOT NULL,
  lower_hall_seats INTEGER NOT NULL,
  upper_gallery_seats INTEGER NOT NULL,
  vip_seats INTEGER NOT NULL DEFAULT 0,       -- up to 10 VIP seats per upper gallery
  UNIQUE(cinema_id, screen_number),
  FOREIGN KEY (cinema_id) REFERENCES cinemas(cinema_id)
);

-- Films
CREATE TABLE films (
  film_id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  description TEXT,
  genre TEXT,
  age_rating TEXT,
  actors TEXT,
  duration_mins INTEGER                       -- runtime in minutes (e.g. 130 for "2h 10m")
);

-- Pricing
CREATE TABLE pricing_rules (
  pricing_id INTEGER PRIMARY KEY AUTOINCREMENT,
  city_id INTEGER NOT NULL,
  show_type TEXT CHECK(show_type IN ('Morning', 'Afternoon', 'Evening')) NOT NULL,
  base_price REAL NOT NULL,
  upper_premium REAL DEFAULT 0.2,
  vip_premium REAL DEFAULT 0.2,
  UNIQUE(city_id, show_type),
  FOREIGN KEY (city_id) REFERENCES cities(city_id)
);

-- Listings (Shows)
-- created_by references users(user_id) so both admins AND managers can
-- create listings.  Role validation is handled in application logic.
CREATE TABLE listings (
  listing_id INTEGER PRIMARY KEY AUTOINCREMENT,
  film_id INTEGER NOT NULL,
  screen_id INTEGER NOT NULL,
  show_date DATE NOT NULL,
  show_time TIME NOT NULL,
  show_type TEXT CHECK(show_type IN ('Morning', 'Afternoon', 'Evening')) NOT NULL,
  created_by INTEGER NOT NULL,
  is_active INTEGER DEFAULT 1,
  UNIQUE(screen_id, show_date, show_time),
  FOREIGN KEY (film_id) REFERENCES films(film_id),
  FOREIGN KEY (screen_id) REFERENCES screens(screen_id),
  FOREIGN KEY (created_by) REFERENCES users(user_id)
);

-- Seats
CREATE TABLE seats (
  seat_id INTEGER PRIMARY KEY AUTOINCREMENT,
  screen_id INTEGER NOT NULL,
  seat_number TEXT NOT NULL,
  seat_type TEXT CHECK(seat_type IN ('lower', 'upper', 'vip')) NOT NULL,
  UNIQUE(screen_id, seat_number),
  FOREIGN KEY (screen_id) REFERENCES screens(screen_id)
);

-- Bookings
CREATE TABLE bookings (
  booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
  booking_ref TEXT UNIQUE NOT NULL,
  listing_id INTEGER NOT NULL,
  staff_id INTEGER NOT NULL,
  booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  num_tickets INTEGER NOT NULL,
  total_cost REAL NOT NULL,
  status TEXT CHECK(status IN ('confirmed', 'cancelled', 'completed')) DEFAULT 'confirmed',
  FOREIGN KEY (listing_id) REFERENCES listings(listing_id),
  FOREIGN KEY (staff_id) REFERENCES users(user_id)
);

-- Booked Seats
CREATE TABLE booked_seats (
  booked_seat_id INTEGER PRIMARY KEY AUTOINCREMENT,
  booking_id INTEGER NOT NULL,
  seat_id INTEGER NOT NULL,
  ticket_type TEXT CHECK(ticket_type IN ('lower', 'upper', 'vip')) NOT NULL,
  price_charged REAL NOT NULL,
  UNIQUE(booking_id, seat_id),
  FOREIGN KEY (booking_id) REFERENCES bookings(booking_id),
  FOREIGN KEY (seat_id) REFERENCES seats(seat_id)
);

-- Cancellations
CREATE TABLE cancellations (
  cancellation_id INTEGER PRIMARY KEY AUTOINCREMENT,
  booking_id INTEGER NOT NULL,
  cancelled_by INTEGER NOT NULL,
  cancel_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  charge_rate REAL DEFAULT 0.5,
  refund_amount REAL NOT NULL,
  FOREIGN KEY (booking_id) REFERENCES bookings(booking_id),
  FOREIGN KEY (cancelled_by) REFERENCES users(user_id)
);

-- Reports
CREATE TABLE reports (
  report_id INTEGER PRIMARY KEY AUTOINCREMENT,
  report_type TEXT NOT NULL,
  generated_by INTEGER NOT NULL,
  generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  data TEXT,
  FOREIGN KEY (generated_by) REFERENCES users(user_id)
);

-- Seed Data
INSERT INTO cities (name) VALUES ('Birmingham'), ('Bristol'), ('Cardiff'), ('London');

-- Pricing Rules per specification
INSERT INTO pricing_rules (city_id, show_type, base_price) VALUES
(1, 'Morning', 5.0), (1, 'Afternoon', 6.0), (1, 'Evening', 7.0),
(2, 'Morning', 6.0), (2, 'Afternoon', 7.0), (2, 'Evening', 8.0),
(3, 'Morning', 5.0), (3, 'Afternoon', 6.0), (3, 'Evening', 7.0),
(4, 'Morning', 10.0), (4, 'Afternoon', 11.0), (4, 'Evening', 12.0);