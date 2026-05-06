# Horizon Cinemas Booking System (HCBS)

![HCBS Banner](https://img.shields.io/badge/HCBS-Cinema%20Booking-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.x-green?style=for-the-badge&logo=python)
![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey?style=for-the-badge&logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

Horizon Cinemas Booking System (HCBS) is a comprehensive, Python-based desktop application designed to streamline the operations of a modern cinema chain. From film scheduling and seat reservations to detailed financial reporting, HCBS provides a robust solution for both customers and cinema staff.

---

## 🌟 Key Features

### 🎞️ Booking Management
*   **Dynamic Seat Selection**: Visual interface for selecting seats across different tiers (Standard, Upper Gallery, VIP).
*   **Flexible Listings**: Browse films by cinema, date, and time.
*   **Automated Receipts**: Generation of booking confirmations and receipts.

### 💰 Advanced Pricing Engine
*   **Tiered Pricing**: Automatic calculation of premiums for Upper Gallery (+20%) and VIP (+44%) seating.
*   **Time-of-Day Pricing**: Support for varying rates based on screening time.

### 🛠️ Administrative & Management Tools
*   **Admin Dashboard**: Manage films, screens, listings, and user accounts.
*   **Manager Insights**: Generate sales reports, analyze top-performing films, and track staff booking activity.
*   **System Seeding**: Automated database initialisation with realistic sample data.

### 🔄 Cancellation & Refunds
*   **Policy Enforcement**: Automated refund calculation (50%) for cancellations made more than 24 hours in advance.

---

## 🏗️ Project Architecture

The project follows a modular structure to ensure maintainability and scalability:

-   `models/`: Data structures and business logic for Films, Bookings, Users, etc.
-   `controllers/`: Intermediate logic handling communication between the UI and Services.
-   `services/`: Core business services (Pricing, Reporting, Authentication).
-   `ui/`: Tkinter-based graphical user interfaces for different user roles.
-   `database/`: Database connection management, schema definitions, and seed scripts.
-   `utils/`: Helper functions for date formatting, validation, and UI styling.

---

## 🚀 Getting Started

### Prerequisites
*   Python 3.8 or higher
*   pip (Python package installer)

### Installation
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/StudyingBelial/horizon-booking-system.git
    cd horizon-booking-system
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application
Launch the system by running the main entry point:
```bash
python main.py
```
*Note: The database will be automatically created and seeded on the first run.*

---

## 🧪 Development & Testing

### Running Tests
We use `pytest` for comprehensive unit and integration testing:
```bash
pytest
```

### Code Quality
Maintain code standards using the following tools:
*   **Formatting**: `black .`
*   **Linting**: `flake8`
*   **Security Scanning**: `bandit -r .`

---

## 👥 Contributors
Developed as part of the **Advanced Software Development** module.
