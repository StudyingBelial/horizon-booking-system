# Horizon Cinemas Booking System (HCBS) — User Manual

Welcome to the **Horizon Cinemas Booking System (HCBS)**. This manual provides a step-by-step guide on how to use the system's features based on your assigned user role.

---

## 🔑 1. Getting Started

### Logging In
1.  Launch the application by running `python main.py`.
2.  On the **Sign In** screen, select your portal (Admin, Manager, or Staff).
3.  Enter your **Username** and **Password**.
    *   *Default credentials for testing: admin/admin123, manager/manager123, staff1/staff123, staff2/staff456.*
4.  Click **SIGN IN**.

---

## 🎟️ 2. Booking Tickets (Staff/Admin/Manager)

The booking interface is used to process customer ticket purchases.

1.  **Select Film**: Use the dropdown to choose the movie the customer wants to see.
2.  **Select Cinema & Listing**: 
    *   Choose the cinema location.
    *   Select the specific screening date and time.
3.  **Choose Seats**:
    *   A colour-coded map will appear on the right.
    *   **Blue**: Standard seating.
    *   **Purple**: Upper Gallery (+20% premium).
    *   **Gold**: VIP (+44% premium).
    *   **Grey**: Already booked.
    *   Click on available seats to select them (they will turn **Green**).
4.  **Confirm Booking**:
    *   Review the **Total Cost** in the summary panel.
    *   Click **Confirm Booking**.
    *   A receipt window will appear with the **Booking Reference**. Provide this to the customer.

---

## ❌ 3. Cancelling a Booking

If a customer requests a refund, follow these steps:

1.  Click **Cancel Booking** from the main booking screen.
2.  Enter the **Booking Reference** (e.g., `HCB-A1B2C3D4`) and click **Look Up**.
3.  The system will display the booking details and check if it is **Eligible** for cancellation.
    *   *Policy: Cancellations must be made at least 24 hours before the showtime.*
4.  If eligible, click **Confirm Cancellation**.
5.  A **50% refund** will be processed, and the seats will be released.

---

## 🛠️ 4. Administrative Tasks (Admin Only)

Administrators have access to the full dashboard to manage system data.

### Managing Listings
*   **Add Listing**: Schedule a film in a specific screen at a specific time.
*   **Edit Listing**: Modify existing schedules.
*   **Delete Listing**: Remove a scheduled showing.

### Managing Films
*   Go to the **Films** tab to add new movies to the database.
*   Required info: Title, Description, Genre, Age Rating, and Actors.

### Viewing All Bookings
*   The **Bookings** tab shows a master list of all reservations made in the system.
*   You can filter by reference or status.

---

## 📊 5. Management & Reports (Manager/Admin)

Managers can track business performance through the **Reports** tab.

1.  **Select Report Type**:
    *   **Bookings**: General booking log.
    *   **Revenue**: Financial breakdown.
    *   **Occupancy**: How full the screens are.
    *   **Top Film**: Which movies are selling best.
    *   **Staff**: Performance tracking for booking staff.
2.  **Filter by Month**: Enter a date in `YYYY-MM` format (optional).
3.  **Generate**: Click the button to view data in the table.
4.  **Export CSV**: Save the report to your computer for further analysis.

---

## 💡 6. Pricing & Seating Policy

HCBS uses a tiered pricing model to maximise revenue:

| Seat Type | Premium | Description |
| :--- | :--- | :--- |
| **Standard** | Base Price | Comfortable seats in the lower hall. |
| **Upper Gallery** | +20% | Elevated seating with a better view. |
| **VIP** | +44% | Premium luxury seating in the gallery. |

*Note: Prices are calculated dynamically based on the listing type (IMAX, 3D, etc.) and the seat category.*

---

## 🆘 Support
For technical issues, please contact the system administrator or refer to the `README.md` for installation troubleshooting.
