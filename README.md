# 💎 GoldFolio — Rojesara Heritage Commercial Jewelry E-Commerce & ERP Platform

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Framework-Django%205.x-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/API-Django%20REST%20Framework-A30000?logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![Database](https://img.shields.io/badge/Database-MySQL%20%7C%20SQLite%20(Auto--Switch)-4479A1?logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Tailwind CSS](https://img.shields.io/badge/Styling-Tailwind%20CSS%20%7C%20Onyx%20%26%20Gold-B8860B?logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Analytics](https://img.shields.io/badge/BI%20Analytics-Matplotlib%20(In--Memory)-11557C?logo=python&logoColor=white)](https://matplotlib.org/)
[![PDF Invoicing](https://img.shields.io/badge/Invoice%20Engine-xhtml2pdf-E34F26)](https://github.com/xhtml2pdf/xhtml2pdf)

> An enterprise-grade, luxury full-stack jewelry marketplace and ERP platform engineered with a **Real-Time Dynamic Metal Pricing Engine**, automated SKU & weight computing, historical purchase price freezing, visual business intelligence charts, and automated GST PDF invoice generation.

---

## 📌 Table of Contents

- [Platform Overview](#-platform-overview)
- [Special Luxury Frontend UI/UX Design](#-special-luxury-frontend-uiux-design)
- [Comprehensive Module Architecture](#-comprehensive-module-architecture)
  - [1. Real-Time Dynamic Metal Pricing Engine](#1-real-time-dynamic-metal-pricing-engine)
  - [2. Historical Price Freezing Engine](#2-historical-price-freezing-engine)
  - [3. Inventory & Automated SKU Generator](#3-inventory--automated-sku-generator)
  - [4. Automated GST PDF Tax Invoice Generator](#4-automated-gst-pdf-tax-invoice-generator)
  - [5. Executive Sales Analytics & BI Visualizer](#5-executive-sales-analytics--bi-visualizer)
  - [6. Customer Shopping & Order Tracking Pipeline](#6-customer-shopping--order-tracking-pipeline)
  - [7. OTP Authentication & Security Suite](#7-otp-authentication--security-suite)
  - [8. Zero-Config Database Switcher (SQLite + MySQL)](#8-zero-config-database-switcher-sqlite--mysql)
- [Dynamic Pricing Mathematical Formula](#-dynamic-pricing-mathematical-formula)
- [Complete System Routes & Page Directory](#-complete-system-routes--page-directory)
- [Tech Stack Architecture](#-tech-stack-architecture)
- [Directory Structure](#-directory-structure)
- [Local Installation & Setup Guide](#-local-installation--setup-guide)
- [Contributors](#-contributors)

---

## 🌟 Platform Overview

Traditional e-commerce platforms operate on fixed product pricing. In contrast, **fine jewelry retailing** deals with daily fluctuating bullion market rates (Gold 24K, 22K, 18K, Silver, Platinum), multi-tier weight accounting (Gross, Net pure metal, and Gemstone weight), Hallmark identification (HUID), making charges, and mandatory tax compliance.

**GoldFolio (Rojesara Heritage)** bridges luxury consumer shopping and robust merchant back-office management into a seamless digital ecosystem.

---

## ✨ Special Luxury Frontend UI/UX Design

The storefront is purpose-built to deliver an elite luxury shopping experience comparable to legacy heritage jewelers:

### 🎨 Visual Theme & Palette
- **Onyx Black (`#0F1016`) & Royal Gold (`#B8860B`):** Premium high-contrast aesthetic with soft alabaster backgrounds (`#FDFCFB`).
- **Frosted Glassmorphism:** Headers, badges, and modals utilize `backdrop-blur-md` with semi-transparent overlays for modern depth.
- **Micro-Interactions & Hover Dynamics:** Product image cards feature smooth 700ms scale zoom (`group-hover:scale-110`), floating status badges, and pulsating discount tags (`animate-pulse`).

### 📱 Interactive Slide-Over Filter Drawer
- Accessible anywhere in the catalog via a slide-over modal with backdrop blur.
- Dual-axis filtering: **Metal Choice** (Gold vs Silver interactive radio tiles) and **Net Weight Range Sliders** (minimum and maximum grams).
- Fast, non-destructive catalog filtering with instant clear-all resets.

### 🖼 Full-Viewport Hero Swiper Banner
- Responsive touch-enabled carousel (`Swiper.js`) highlighting seasonal launches (e.g. *The Heritage Collection*).
- Typography featuring animated fade-in headlines with generous letter spacing (`tracking-[0.4em]`).

### 🔍 Transparent Product Specification Matrix
Each product detail page breaks down jewelry anatomy into an easy-to-read 4-quadrant layout:
- **Purity Indicator:** Clear karat marking (`18K`, `22K`, `24K`).
- **Net Weight:** Pure precious metal weight in grams (used directly for bullion valuation).
- **Stone / Other Weight:** Embedded gemstones or diamond weight.
- **Gross Weight:** Total physical weight automatically calculated on upload.
- **HUID Code:** Hallmark Unique Identification code verifying government lab authenticity.
- **Interactive Price Card:** Transparent cost breakdown showing the exact live rate per gram, metal value, making charges, 8% GST, and discount savings.

---

## 🏗 Comprehensive Module Architecture

```
                          ┌────────────────────────────────────────────────────────┐
                          │         Rojesara Heritage Storefront UI (HTML5/Tailwind)│
                          │   • Luxury Catalog  • Filter Drawer  • Live Calculator │
                          │   • Dynamic Cart    • Express Checkout • User Profile  │
                          └───────────────────────────┬────────────────────────────┘
                                                      │ HTTP / Form Submissions
                                                      ▼
                          ┌────────────────────────────────────────────────────────┐
                          │               Django 5.x Web Application Engine        │
                          ├───────────────────────────┬────────────────────────────┤
                          │  Customer Operations      │  Merchant Admin ERP        │
                          │  • OTP Authentication     │  • Daily Metal Rate Setter │
                          │  • Persistent Cart        │  • SKU Auto-Generation     │
                          │  • Historical Price Lock  │  • Stock Alert Monitor     │
                          │  • PDF Invoice Download   │  • Matplotlib BI Plots     │
                          └─────────────┬─────────────┴─────────────┬──────────────┘
                                        │                           │
                                        ▼                           ▼
                         ┌─────────────────────────────┐  ┌─────────────────────────┐
                         │   Automated Engines         │  │   Zero-Config Database  │
                         │   • xhtml2pdf Invoice       │  │   • SQLite (Dev Default)│
                         │   • Matplotlib In-Memory    │  │   • MySQL (Production)  │
                         │   • SMTP OTP Mailer         │  │   • Auto-fallback logic │
                         └─────────────────────────────┘  └─────────────────────────┘
```

---

### 1. Real-Time Dynamic Metal Pricing Engine
- **Centralized Daily Rates (`MetalRate` Model):** Store owners update the global price per gram for **Gold 24K, Gold 22K, Gold 18K, Silver, and Platinum** from a single control screen (`/dashboard/set-rates/`).
- **Zero-Overwrite Live Revaluation:** Instead of writing new prices to every row in the database, the `Product.price_details` property computes the exact current market price on-the-fly whenever a user browses the catalog.

### 2. Historical Price Freezing Engine
- **Accounting & Audit Protection:** In standard e-commerce, if a master product price changes, naive databases risk mutating past order records.
- **Locked Purchase Snapshot (`OrderItem` Model):** When a purchase completes, the exact price paid is saved into `price_at_purchase`. Future increases or drops in bullion gold rates will **never** alter previous customer receipts or historical revenue ledgers.

### 3. Inventory & Automated SKU Generator
- **Pre-Save Signals & Computation:**
  - Auto-calculates `Gross Weight = Net Weight + Stone Weight`.
  - Auto-mints structured SKUs based on classification: `prefix = MET-CAT` ➔ Next sequential number (e.g. `GOL-NEC-001`, `SIL-RIN-002`).
  - Auto-generates unique, collision-proof SEO URL slugs (`slugify`).
- **Stock Depletion & Low-Stock Alerts (`/dashboard/alerts/`):** Visual indicators notifying managers when inventory reaches critical threshold or is marked sold out.

### 4. Automated GST PDF Tax Invoice Generator
- **Engineered with `xhtml2pdf` (pisa):** Generates official, legal A4 PDF tax invoices on demand.
- **Comprehensive Invoice Elements:**
  - Official branding: **Rojesara Heritage — Legacy of Pure Gold & Diamond Jewellery**.
  - Customer shipping and billing address snapshot.
  - Unique Order ID (e.g. `ORD-849201`), transaction timestamp, and payment method (COD, UPI, Card).
  - Itemized table with description, purity, HUID number, net weight, metal rate applied, making charges, 8% GST, and grand total.

### 5. Executive Sales Analytics & BI Visualizer
- **In-Memory Matplotlib Pipeline (`products/utils.py`):** Runs headless using the `Agg` backend — charts are rendered directly into memory buffers, base64 encoded, and injected into templates without saving temporary image files to disk.
- **30-Day Sales Trend Curve:** Continuous revenue trajectory with rotated date labels and automated grid markers.
- **Two-Week Comparative Battle Analysis:** Form-driven date selector plotting **Week 1 (Gold `#b8860b`)** against **Week 2 (Onyx `#333333`)** with automated growth percentage calculation (`▲ +X%` / `▼ -X%`).

### 6. Customer Shopping & Order Tracking Pipeline
- **Real-Time Dynamic Cart (`Cart` & `CartItem`):** Synchronizes items per user with instant quantity increment/decrement calculations.
- **Multi-Step Checkout Flow:** Captures complete delivery address snapshot and payment options.
- **Customer Account Dashboard (`/account/profile/`):** Displays previous orders, real-time fulfillment status (`Pending`, `Placed`, `Shipped`, `Delivered`, `Cancelled`), and 1-click invoice re-download.

### 7. OTP Authentication & Security Suite
- **Two-Factor Email OTP (`OTPVerifier` Model):** 6-digit random verification code delivered directly to the user's email inbox with a strict **2-minute expiration window**.
- **Cryptographic Security:** Built-in Django password hashing, CSRF token validation on every POST request, and protected admin routes restricted to verified superusers.

### 8. Zero-Config Database Switcher (SQLite + MySQL)
- **Zero-Error Local Development:** By default, cloning and running the repository connects to a local `db.sqlite3` file with **zero setup required**.
- **Enterprise MySQL Production Ready:** When running with XAMPP or a remote MySQL server, simply setting `DB_NAME=goldfolio_db` in `.env` automatically routes queries to MySQL without editing any codebase files.

---

## 🧮 Dynamic Pricing Mathematical Formula

The transparent pricing engine executes the following formula:

$$\text{Metal Cost} = \text{Net Weight (grams)} \times \text{Current Metal Rate per Gram}$$

$$\text{Base Total} = \text{Metal Cost} + \text{Making Charges} + \text{Auxiliary Charges}$$

$$\text{Price with Tax} = \text{Base Total} \times 1.08 \quad (\text{8\% GST})$$

$$\text{Final Payable Price} = \text{Price with Tax} - \left(\text{Price with Tax} \times \frac{\text{Discount \%}}{100}\right)$$

---

## 🗺 Complete System Routes & Page Directory

| URL Route | View Handler | Role & Description |
| :--- | :--- | :--- |
| `/` | `home_view` | Luxury customer storefront, filters, and collections |
| `/product/<slug>/` | `product_detail` | Detailed specifications, dynamic pricing breakdown |
| `/cart/` | `view_cart` | Active cart items, price summary, and item removal |
| `/cart/add/<id>/` | `add_to_cart` | Adds selected item to cart with quantity tracking |
| `/checkout/` | `checkout` | Shipping address entry and payment method selection |
| `/order-success/<id>/` | `order_success_view` | Order confirmation screen with tracking ID |
| `/download-invoice/<id>/` | `download_invoice` | Generates and downloads official GST PDF invoice |
| `/account/profile/` | `user_profile` | Order history, order status, and re-download invoice |
| `/dashboard/` | `dashboard_home` | Merchant overview, revenue KPIs, and recent orders |
| `/dashboard/add/` | `add_stock` | Add new jewelry item with auto-weight and SKU |
| `/dashboard/edit/<id>/` | `edit_stock` | Modify product pricing, discount, or weight values |
| `/dashboard/delete/<id>/` | `delete_stock` | Remove stock item from catalog |
| `/dashboard/mark-sold/<id>/`| `mark_as_sold` | Toggle item between Available and Sold Out |
| `/dashboard/set-rates/` | `set_rates` | Update daily bullion rates for Gold, Silver, Platinum |
| `/dashboard/alerts/` | `stock_alerts_view` | Low stock inventory warning dashboard |
| `/dashboard/analysis/` | `stock_analysis` | Composition breakdown of inventory by metal and category |
| `/dashboard/analytics/` | `sales_analytics` | 30-day and 2-week comparative visual sales charts |
| `/admin-panel/orders/` | `manage_orders` | Order management dashboard with status updater |
| `/auth/` | `auth_view` | Customer sign-in / registration screen |
| `/auth/send-otp/` | `send_otp` | Generates and dispatches 6-digit email verification code |
| `/auth/verify-otp/` | `verify_otp` | Validates OTP code within 2-minute time window |
| `/auth/create-account/` | `create_account` | Registers new customer account |
| `/auth/logout/` | `logout_view` | Terminates user session |

---

## 💻 Tech Stack Architecture

| Layer | Technologies Used | Key Responsibilities |
| :--- | :--- | :--- |
| **Frontend UI** | HTML5, CSS3, Tailwind CSS, JavaScript | Luxury gold aesthetic, filter drawer, responsive grid |
| **Interactive Components** | Swiper.js, Hero banners, Glassmorphism | Smooth carousel and interactive price cards |
| **Backend Framework** | Python 3.x, Django 5.x | Core MVT business logic, authentication, ORM |
| **API Layer** | Django REST Framework (DRF) | RESTful endpoints for catalog and cart operations |
| **Database** | MySQL (XAMPP) / SQLite3 (Auto-detect) | Multi-table relational schema with foreign key integrity |
| **Data Visualization** | Matplotlib (Agg headless engine) | In-memory base64 encoded business intelligence plots |
| **PDF Compilation** | xhtml2pdf (pisa) | Official GST tax invoice generation |
| **Security & Email** | Django Auth, SMTP, Custom OTP Verifier | Salted passwords, CSRF protection, expiring OTPs |

---

## 📁 Directory Structure

```plaintext
Jewelery-Shop-Website/
├── backend/                   # Core Django project configuration
│   ├── asgi.py                # Asynchronous server gateway
│   ├── settings.py            # Settings with Smart Database Switcher (SQLite/MySQL)
│   ├── urls.py                # Global master routing directory
│   └── wsgi.py                # WSGI web server deployment gateway
├── products/                  # Core commercial jewelry application
│   ├── migrations/            # 10+ sequential database migration versions
│   ├── admin.py               # Django administrative model definitions
│   ├── models.py              # Product, MetalRate, Order, Cart, Profile, OTPVerifier
│   ├── utils.py               # Matplotlib in-memory visual plot generators
│   ├── views.py               # All 25+ view handlers, pricing logic, invoice compiler
│   └── urls.py                # Product and dashboard route rules
├── static/                    # Compiled luxury stylesheets, brand images, JavaScript
├── templates/                 # Server-rendered HTML templates
│   ├── admin_panel/           # Order management and sub-admin controls
│   ├── auth/                  # Authentication modals and OTP inputs
│   ├── emails/                # Order receipt and OTP transactional HTML emails
│   ├── base.html              # Master layout with luxury navigation and footer
│   ├── index.html             # Homepage with hero slider and filter drawer
│   ├── product_detail.html    # Product specs, 4-quadrant weights, and price card
│   ├── cart.html              # Dynamic shopping cart with real-time recalculations
│   ├── checkout.html          # Shipping address capture and payment options
│   ├── invoice.html           # Official printable PDF tax invoice template
│   ├── sales_analytics.html   # BI sales comparison charts and growth indicators
│   ├── set_rates.html         # Daily bullion metal rate control tool
│   ├── stock_alerts.html      # Inventory depletion warning views
│   └── user_profile.html      # Customer order history and invoice re-download
├── .env.example               # Sample environment configuration
├── .gitignore                 # Standard exclusions (SQLite, media, cache)
├── manage.py                  # Django command-line interface
├── requirements.txt           # Python dependency specifications
└── README.md                  # Comprehensive platform documentation
```

---

## ⚡ Local Installation & Setup Guide

### Prerequisites
- **Python 3.10 or higher**
- **Git**
- *(Optional)* **XAMPP / MySQL** if you wish to run on MySQL instead of SQLite.

---

### Step 1: Clone the Repository
```bash
git clone https://github.com/mayank122340/Jewelery-Shop-Website.git
cd Jewelery-Shop-Website
```

### Step 2: Create and Activate a Virtual Environment
```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run Migrations
*(Runs instantly on SQLite by default — no database setup needed)*
```bash
python manage.py migrate
```

### Step 5: Create a Superuser (Admin)
```bash
python manage.py createsuperuser
```

### Step 6: Start the Server
```bash
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

### (Optional) Running with MySQL & XAMPP
To connect to MySQL instead of SQLite:
1. Create a `.env` file in the project root:
   ```env
   DB_NAME=goldfolio_db
   DB_USER=root
   DB_PASSWORD=
   DB_HOST=127.0.0.1
   DB_PORT=3306
   ```
2. Open the **XAMPP Control Panel**, start **Apache** and **MySQL**, and create a database named `goldfolio_db` in phpMyAdmin.
3. Run `python manage.py migrate` and start the server.

---

## 🤝 Contributors

- **Mayank Rojesara** ([@mayank122340](https://github.com/mayank122340)) — Full-Stack Architecture, Dynamic Metal Pricing Engine, Database Modeling, In-Memory BI Analytics & Luxury Frontend Design
