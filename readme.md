# 🏟️ Sporting Club Reservation Service

A full-featured **Odoo module** for managing reservations, memberships, facilities, and scheduling across sporting clubs.
This module provides a complete digital management system for clubs, trainers, and members — including payments, analytics, and automated scheduling.

---

## 🧾 Module Overview

The **Sporting Club Reservation Service** module allows clubs to efficiently manage their operations:

* 🧍 Member profiles and subscriptions
* 🕒 Facility reservations (courts, fields, halls, etc.)
* 📅 Scheduling and trainer availability
* 💰 Reservation payments and invoicing
* 📊 Reporting and analytics

Its goal is to streamline club operations, automate administrative workflows, and enhance customer experience.

---

## ⚙️ Module Metadata

| Field                     | Value                                                                                                                        |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| **Name**                  | Sporting Club Reservation Service                                                                                            |
| **Summary**               | Manage reservations, memberships, and scheduling for sporting clubs.                                                         |
| **Author**                | Karim Mohammed Aboelazm                                                                                                      |
| **Website**               | [https://www.yourcompany.com](https://www.yourcompany.com)                                                                   |
| **Category**              | Services / Reservation                                                                                                       |
| **License**               | LGPL-3                                                                                                                       |
| **Version**               | 0.1                                                                                                                          |
| **Depends On**            | `base`, `contacts`, `base_cities`, `mail`, `product`, `account`, `payment`, `base_geolocalize`, `sale`, `web`, `auth_signup` |
| **External Dependencies** | `jwt`                                                                                                                        |
| **Application**           | ✅ True                                                                                                                       |
| **Installable**           | ✅ True                                                                                                                       |

---

## 🏗️ Key Features

### 🔹 Membership Management

* Manage club members, subscription plans, and renewals
* Integration with contact and user records (`res.partner`, `res.users`)

### 🔹 Facility Reservation

* Manage courts, fields, halls, pools, and other facilities
* Real-time reservation calendar with conflict prevention
* Integrated with Odoo’s scheduling and booking wizards

### 🔹 Trainer and Session Management

* Define trainers, assign schedules and sessions
* Manage session durations, sports categories, and performance tracking

### 🔹 Pricing and Promotions

* Flexible pricing rules per sport, facility, or member type
* Create promotions, discounts, and coupon-based offers

### 🔹 Payments and Accounting

* Linked to Odoo’s `account` and `payment` modules
* Auto-generate invoices per reservation
* Integration with Odoo Sale Orders and Payment Acquirers

### 🔹 Reporting and Analytics

* Reservation Revenue Report
* Club Overview Report
* Facility Utilization and Performance Report

---

## 📂 Module Structure

```
sport_club_reservation/
│
├── security/
│   ├── club_sport_security.xml
│   ├── ir.model.access.csv
│
├── data/
│   ├── ir.sequence.xml
│   ├── ir_cron_data.xml
│
├── views/
│   ├── res_partner_inherit_view.xml
│   ├── res_users_inherit_view.xml
│   ├── sport_club_model_view.xml
│   ├── sport_club_sport_view.xml
│   ├── sport_club_policy_view.xml
│   ├── sport_club_facility_view.xml
│   ├── sport_club_calendar_view.xml
│   ├── sport_club_pricing_rule_views.xml
│   ├── sport_club_promotion_views.xml
│   ├── sport_club_equipments_view.xml
│   ├── sport_club_reservation_views.xml
│   ├── sport_club_trainer_views.xml
│   ├── sport_club_training_session_views.xml
│   ├── sport_club_equipment_booking_views.xml
│   └── menus.xml
│
├── wizard/
│   ├── generate_calendar_times_view.xml
│   ├── reservation_revenue_wizard_view.xml
│   ├── sport_club_reports_view.xml
│   └── sport_club_facility_reports_view.xml
│
├── report/
│   ├── report_template_base.xml
│   ├── reservation_revenue_report_template.xml
│   ├── sport_club_overview_report_template.xml
│   └── sport_club_facility_report_template.xml
│
└── __manifest__.py
```

---

## 🧰 Installation Guide

### Step 1: Prerequisites

Ensure the following are installed and active:

* Python 3.10+
* Odoo 18 (Enterprise or Community)
* PostgreSQL database
* Python package:

  ```bash
  pip install pyjwt
  ```

### Step 2: Installation

1. Copy the module folder into your Odoo addons path.
   Example:

   ```
   /odoo/custom_addons/sport_club_reservation/
   ```
2. Restart your Odoo service:

   ```bash
   ./odoo-bin -u all
   ```
3. Activate **Developer Mode** in Odoo UI.
4. Navigate to **Apps → Update Apps List → Install** the module **Sporting Club Reservation Service**.

---

## 📡 Optional API Integration

This module can optionally integrate with the **Sports Reservation API** project (see `sports_api` module) to expose endpoints for:

* `/api/login`
* `/api/club/search/all`
* `/api/trainer/filter`
* `/api/reservation/create`
* `/api/player/search/one`

This allows external systems or mobile apps to connect via JWT and Odoo Session Authentication.

---

## 🧮 Scheduled Actions

The module includes cron jobs (`ir.cron`) to:

* Auto-generate facility calendars.
* Auto-cancel expired reservations.
* Send daily summary reports to managers.

---

## 🪪 License

**License:** LGPL-3
You are free to use, modify, and distribute this module under the terms of the **GNU Lesser General Public License v3**.

---

## 👨‍💻 Author

**Developed by:**
**Karim Mohammed Aboelazm**
📧 Email: [karim@gmail.com](mailto:karimaboelazm6@gmail.com)

---

## 🧠 Summary

This module transforms manual club management into a digital, automated, and integrated experience — supporting end-to-end workflows from member registration to facility reservation and revenue analytics.
