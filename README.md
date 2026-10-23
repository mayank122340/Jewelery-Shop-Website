# 💎 GoldFolio — Commercial Jewelry E-Commerce & ERP Platform

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Framework-Django%205.x-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/API-Django%20REST%20Framework-A30000?logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![MySQL](https://img.shields.io/badge/Database-MySQL-4479A1?logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Matplotlib](https://img.shields.io/badge/Analytics-Matplotlib-11557C?logo=python&logoColor=white)](https://matplotlib.org/)
[![PDF Engine](https://img.shields.io/badge/Invoice-xhtml2pdf-E34F26)](https://github.com/xhtml2pdf/xhtml2pdf)

> An end-to-end, full-stack commercial jewelry marketplace and enterprise resource planning (ERP) system featuring a **Real-Time Dynamic Metal Pricing Engine**, automated SKU & weight calculations, historical purchase price freezing, visual sales analytics, and automated GST PDF invoice dispatch.

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Dynamic Pricing Engine Formula](#-dynamic-pricing-engine-formula)
- [Tech Stack](#-tech-stack)
- [Directory Structure](#-directory-structure)
- [Admin Analytics & Business Intelligence](#-admin-analytics--business-intelligence)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Local Installation](#local-installation)
  - [Environment Configuration (.env)](#environment-configuration-env)
  - [Database Migration & Superuser](#database-migration--superuser)
  - [Running the Development Server](#running-the-development-server)
- [Core Workflows](#-core-workflows)
- [Contributors](#-contributors)

---

## 🌟 Overview

Jewelry retail differs fundamentally from conventional e-commerce: product prices fluctuate continuously with volatile gold, silver, and platinum market rates, products have intricate weight compositions (Gross, Net, Stone), and regulatory invoicing requires precise itemization of making charges, hallmark identification (HUID), and GST.

**GoldFolio** provides jewelry merchants and customers with:
- **For Customers:** A luxury digital showroom with category browsing, real-time live price recalculations, OTP authentication, persistent cart/wishlist, and 1-click PDF invoice downloads.
- **For Merchants / Admins:** Centralized daily metal rate control (Gold 24K, 22K, 18K, Silver, Platinum), automated SKU generation, visual sales analytics graphs, inventory stock alerts, and order lifecycle management.

---

## 🚀 Key Features

### ⚖️ Real-Time Dynamic Metal Pricing Engine
- **Global Rate Controller:** Superadmins update daily metal prices per gram through a dedicated dashboard tool.
- **Instant Product Revaluation:** Every item’s price dynamically recalculates across the catalog based on its pure metal weight without manual database overwrites.
- **Freeze-Price Order Integrity:** Once an order is placed, historical transactions permanently lock the `price_at_purchase`, shielding completed orders from subsequent daily rate changes.

### 📦 Inventory & Automated SKU Logic
- **Precision Weight Accounting:** Auto-calculates `Gross Weight = Net Weight + Stone Weight` on pre-save hooks.
- **Intelligent SKU Minting:** Auto-generates structured SKUs based on metal type and category prefix (e.g., `GOL-NEC-001`, `SIL-RIN-004`).
- **Hallmark & Certification:** Integrated HUID (Hallmark Unique Identification) field for verified purity authentication.
- **Stock Depletion Warnings:** Dedicated alerts dashboard notifying managers when high-demand collections run low.

### 📄 Automated GST Tax Invoice Generation
- **Server-Side PDF Rendering:** Uses `xhtml2pdf` to compile official, printable PDF invoices on checkout completion.
- **Detailed Financial Breakdown:** Itemizes base metal rate, pure weight, making charges, auxiliary costs, GST percentage, and applied promotional discounts.

### 📊 Business Intelligence & Sales Analytics
- **Visual Performance Plots:** Leverages `matplotlib` (Agg headless backend) to generate 30-day sales trend graphs and 2-week comparative performance charts.
- **Base64 Image Streaming:** Charts are rendered into memory buffers and embedded into the admin template without writing temporary image files to disk.

### 🔐 Secure OTP-Based Authentication
- **Email Verification Codes:** 6-digit OTP dispatch powered by Django email backends with a strict 2-minute validity timer.
- **Extended User Profiles:** Customer addresses, phone contacts, cities, and pincodes automatically populate checkout forms.

---

## 🏗 System Architecture

```
                       ┌────────────────────────────────────────┐
                       │     Luxury Storefront (HTML5/CSS3/JS)   │
                       │  Catalog • Dynamic Cart • PDF Invoice  │
                       └───────────────────┬────────────────────┘
                                           │  HTTP / Form Post
                                           ▼
                       ┌────────────────────────────────────────┐
                       │         Django 5.x Web Application     │
                       ├────────────────────────────────────────┤
                       │  • Metal Rate Controller & Pricing     │
                       │  • Historical Price Freeze Logic       │
                       │  • Matplotlib Sales Chart Generator    │
                       │  • xhtml2pdf Document Compiler         │
                       └───────────────┬────────────────┬───────┘
                                       │                │
                                       ▼                ▼
                     ┌───────────────────┐    ┌───────────────────┐
                     │  MySQL / SQLite   │    │  SMTP Mail Server │
                     │  Relational Store │    │  OTP & Receipts   │
                     └───────────────────┘    └───────────────────┘
```

---

## 🧮 Dynamic Pricing Engine Formula

The catalog applies the following transparent mathematical formula for every customer view:

$$\text{Metal Cost} = \text{Net Weight (g)} \times \text{Live Metal Rate per Gram}$$

$$\text{Base Total} = \text{Metal Cost} + \text{Making Charges} + \text{Other Charges}$$

$$\text{Price with Tax} = \text{Base Total} \times (1 + \text{GST}_{\text{8\%}})$$

$$\text{Final Price} = \text{Price with Tax} - \left(\text{Price with Tax} \times \frac{\text{Discount \%}}{100}\right)$$

---

## 💻 Tech Stack

| Domain | Technology | Description |
| :--- | :--- | :--- |
| **Backend Framework** | Python 3.x, Django 5.x | High-level web framework following MVT architecture |
| **REST APIs** | Django REST Framework (DRF) | Scalable endpoints for catalog and inventory operations |
| **Database** | MySQL (Production) / SQLite (Local Dev) | Relational database handling transactions and relations |
| **Data Visualization** | Matplotlib (Agg Engine) | In-memory 30-day sales trend and comparative line charts |
| **Document Generation** | xhtml2pdf (pisa) | HTML-to-PDF compiler for automated GST invoices |
| **Security & Auth** | Django Auth + Custom OTP Verifier | Salted password hashing, sessions, and expiring OTPs |
| **Frontend & UI** | HTML5, CSS3, JavaScript, Bootstrap | Luxury gold-and-black themed responsive storefront |

---

## 📁 Directory Structure

```plaintext
Jewelery-Shop-Website/
├── backend/                  # Root Django project configuration
│   ├── asgi.py               # ASGI application entrypoint
│   ├── settings.py           # Core settings, database connectors, and middleware
│   ├── urls.py               # Global routing table
│   └── wsgi.py               # WSGI web server gateway
├── products/                 # Main business logic application
│   ├── migrations/           # Database schema migrations
│   ├── admin.py              # Django admin registration
│   ├── models.py             # Data models (Product, MetalRate, Order, Cart, Profile)
│   ├── utils.py              # Matplotlib chart visualizer & base64 encoding helpers
│   ├── views.py              # Storefront views, admin controllers, checkout, PDF invoice
│   └── urls.py               # Product and shopping routing rules
├── static/                   # Compiled CSS, luxury branding assets, JavaScript
├── templates/                # Server-rendered HTML templates
│   ├── admin_panel/          # Stock and order management views
│   ├── auth/                 # Login, registration, and OTP verification modals
│   ├── emails/               # Transactional HTML email templates
│   ├── index.html            # Primary landing page and category showcase
│   ├── product_detail.html   # Detailed jewelry specs and dynamic price calculation
│   ├── cart.html             # Real-time cart state with price breakdowns
│   ├── checkout.html         # Delivery details and multi-channel payment flow
│   ├── invoice.html          # PDF-printable official tax invoice template
│   └── sales_analytics.html  # Executive BI dashboard with charts
├── .env.example              # Sample environment configuration
├── .gitignore                # Git exclusions
├── manage.py                 # Django command-line executable
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

---

## 📊 Admin Analytics & Business Intelligence

The merchant back-office provides visual reporting powered by `products/utils.py`:
1. **30-Day Sales Trend:** Line graph tracking daily revenue trajectory with rotated timestamps and adaptive grid spacing.
2. **Two-Week Comparative Analysis:** Dual-line overlay comparing current week sales (Gold accent `#b8860b`) against previous week performance (Monochrome `#333333`).
3. **Stock Health Indicators:** Categorical breakdown of in-stock versus sold-out inventory.

---

## ⚡ Getting Started

### Prerequisites
- **Python 3.10+** (Python 3.11 or higher recommended)
- **Git**
- **MySQL Server** (via XAMPP, WampServer, or native MySQL daemon) — *or SQLite for quick evaluation*

---

### Local Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mayank122340/Jewelery-Shop-Website.git
   cd Jewelery-Shop-Website
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

### Environment Configuration (.env)

Create a `.env` file in the root directory based on `.env.example`:

```env
DJANGO_SECRET_KEY=your_generated_secret_key_here
DJANGO_DEBUG=True

# Database Configuration (MySQL / XAMPP)
DB_NAME=goldfolio_db
DB_USER=root
DB_PASSWORD=
DB_HOST=127.0.0.1
DB_PORT=3306

# Email Settings (for OTP & Order Notifications)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

> **Note for XAMPP Users:** Start Apache and MySQL from the XAMPP Control Panel and create a database named `goldfolio_db` via phpMyAdmin.

---

### Database Migration & Superuser

1. **Apply migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Create an Administrator Account:**
   ```bash
   python manage.py createsuperuser
   ```

---

### Running the Development Server

Start the local server:
```bash
python manage.py runserver
```

- **Customer Storefront:** Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Daily Metal Rates Controller:** Visit [http://127.0.0.1:8000/set-rates/](http://127.0.0.1:8000/set-rates/)
- **Executive Sales Analytics:** Visit [http://127.0.0.1:8000/sales-analytics/](http://127.0.0.1:8000/sales-analytics/)
- **Django Admin Portal:** Visit [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 🔄 Core Workflows

1. **Rate Initialization:** The store owner accesses `/set-rates/` to configure live prices per gram for 24K, 22K, 18K Gold, Silver, and Platinum.
2. **Catalog Browsing:** The buyer browses jewelry collections; all prices reflect live metal rates plus making charges and GST.
3. **Cart & Authentication:** The user adds products to their cart and verifies their account via email OTP.
4. **Checkout & Purchase:** An order is finalized, generating a unique order ID (e.g. `ORD-849201`).
5. **Price Locking:** The purchase price is saved in `OrderItem`, ensuring historical financial accuracy regardless of future market fluctuations.
6. **Invoice Generation:** A tax invoice PDF is generated and downloaded instantly by the customer.

---

## 🤝 Contributors

- **Mayank Rojesara** ([@mayank122340](https://github.com/mayank122340)) — Full-Stack Development, Dynamic Pricing Engine, Database Architecture & UI Design
