# 👕 ERA — Smart Wardrobe Manager

> A modern, full-featured clothing management system built with Django. Designed for boutiques, clothing businesses, and inventory managers — ERA bridges the gap between inventory management and customer interaction in one elegant platform.

[![Django](https://img.shields.io/badge/Django-5.1.4-092E20?logo=django)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📋 Table of Contents

- [Why This Exists](#why-this-exists)
- [Features](#features)
- [Screenshots](#screenshots)
- [Tech Stack](#tech-stack)
- [Installation & Setup](#installation--setup)
- [Running the Project](#running-the-project)
- [Environment Variables](#environment-variables)
- [Project Structure](#project-structure)
- [URL Routes](#url-routes)
- [Admin Panel](#admin-panel)
- [Contributing](#contributing)
- [License](#license)

---

## Why This Exists

Managing clothing inventory, handling customer orders, and maintaining a seamless shopping experience is hard. ERA solves this by providing:

- **A customer-facing storefront** where users browse, search, filter, and purchase clothing items with cart and checkout functionality.
- **An admin dashboard** for managing categories, products, orders, users, coupons, and inventory — all from a single interface.
- **Built-in features** like wishlists, product ratings, coupon discounts, order tracking, and newsletter subscriptions — so you don't need third-party plugins for the basics.

---

## Features

### 👤 Customer Features

| Feature | Description |
|---------|-------------|
| **Browse & Search** | Filter products by category, search by name/description, sort by price or date, and filter by price range |
| **Product Details** | View full product info with images, sizes, colors, ratings, reviews, and related products |
| **Shopping Cart** | Add/remove items, update quantities, and view live cart totals via AJAX |
| **Checkout** | Enter shipping details, apply coupon codes, and place orders with auto-generated tracking numbers |
| **Order History** | View past orders, track status, and cancel pending/processing orders |
| **Wishlist** | Save favorite items and manage your wishlist |
| **Ratings & Reviews** | Rate products 1–5 stars and leave written reviews |
| **User Profile** | Manage your account details and view order history |
| **Newsletter Signup** | Subscribe to the store newsletter |

### 🛠️ Admin Features

| Feature | Description |
|---------|-------------|
| **Category CRUD** | Add, edit, delete, and list clothing categories |
| **Product CRUD** | Upload products with images, prices, categories, sizes, colors, and stock quantities |
| **Image Import** | Download product images from external URLs directly into the system |
| **Order Management** | View all orders, update status (Pending → Processing → Shipped → Delivered → Cancelled), edit orders |
| **User Management** | View registered customers and their order history |
| **Coupon System** | Create discount coupons with expiry dates, minimum order values, and percentage discounts |
| **Inventory Tracking** | Monitor stock levels and toggle product active/inactive status |
| **CSV Export** | Export order data to CSV for reporting |
| **Dashboard Analytics** | View key metrics at a glance |
| **Django Admin** | Full access to all models via Django's built-in admin panel with Jet theme |

---

## Screenshots

> 📸 *Screenshots coming soon. The following sections will include visual previews:*

- **Landing Page** — Hero section and featured categories
- **Shop Page** — Product grid with search, filters, and pagination
- **Product Detail** — Full product view with ratings and reviews
- **Cart & Checkout** — Shopping cart and order placement flow
- **Admin Dashboard** — Inventory and order management overview
- **Django Admin (Jet)** — Enhanced admin interface

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Django 5.1.4 (Python) |
| **Frontend** | HTML5, CSS3, Bootstrap 5, JavaScript (AJAX) |
| **Database** | SQLite 3 (default, swappable to PostgreSQL) |
| **Authentication** | Custom session-based auth with Django Auth |
| **Admin Theme** | Django Jet Reboot |
| **Forms** | Crispy Forms + Bootstrap 5 |
| **Image Processing** | Pillow 11.0.0 |
| **Email** | Django SMTP Backend (Gmail) |
| **Environment** | python-decouple for config management |

### Prerequisites

- **Python 3.10+**
- **pip** (Python package manager)
- **Git** (optional, for cloning)
- **SQLite 3** (included with Python; no separate install needed)

---

## Installation & Setup

Follow these steps to get ERA running on your local machine.

### Step 1: Clone or Download the Project

```bash
cd "E:\My Projects\ERA Project\Cloth-Management-System"
```

> If you're starting fresh from a repository:
> ```bash
> git clone <repository-url>
> cd Cloth-Management-System
> ```

### Step 2: Create and Activate a Virtual Environment

It is strongly recommended to use a virtual environment to isolate dependencies.

```bash
# Create virtual environment
python -m venv .venv

# Activate on Windows
.venv\Scripts\activate

# Activate on macOS / Linux
# source .venv/bin/activate
```

You should see `(.venv)` prefixed in your terminal prompt.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs all required packages: Django, Pillow, crispy-forms, django-jet-reboot, python-decouple, and requests.

### Step 4: Configure Environment Variables

The project uses `.env` for configuration. A template is already provided.

1. Copy the `.env` file if needed (it already exists in the project root).
2. Update the values:

```env
# Email Configuration (Gmail SMTP)
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_app_password_here

# Django Secret Key (generate a new one for production)
DJANGO_SECRET_KEY=your-secret-key-here

# Debug Mode (set to False in production)
DJANGO_DEBUG=True

# Allowed Hosts (comma-separated, no spaces)
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

> **Generating a Secret Key**: Run `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` to generate a new key.

> **Gmail App Password**: You'll need to create an [App Password](https://myaccount.google.com/apppasswords) in your Google Account settings if using Gmail for email notifications.

### Step 5: Run Database Migrations

Apply Django migrations to set up the database schema:

```bash
python manage.py makemigrations
python manage.py migrate
```

This creates all necessary tables for products, categories, customers, orders, cart, ratings, wishlists, coupons, and newsletters.

### Step 6: Create a Superuser (Admin Access)

Create an admin account to access the Django admin panel:

```bash
python manage.py createsuperuser
```

You'll be prompted for a username, email, and password. Use a strong password in production.

> **Default Admin Login**: The system also recognizes `admin@era.com` as an admin email for the custom login system. You can create a customer with this email or modify it in `app/views.py`.

### Step 7: Collect Static Files (Production Only)

For production deployment, collect all static files:

```bash
python manage.py collectstatic
```

> Skip this step for local development — Django's development server handles static files automatically when `DEBUG = True`.

---

## Running the Project

Start the Django development server:

```bash
python manage.py runserver
```

The application will be available at:

| Page | URL |
|------|-----|
| **Landing Page** | http://127.0.0.1:8000/ |
| **Shop / Store** | http://127.0.0.1:8000/shopping |
| **Django Admin** | http://127.0.0.1:8000/admin/ |
| **Custom Login** | http://127.0.0.1:8000/login |
| **Sign Up** | http://127.0.0.1:8000/signup |

> To run on a different port: `python manage.py runserver 8080`

---

## Environment Variables

All configuration is managed through the `.env` file using `python-decouple`. Here's a full reference:

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DJANGO_SECRET_KEY` | `string` | *(insecure default)* | Django's cryptographic signing key. **Must be changed in production.** |
| `DJANGO_DEBUG` | `bool` | `True` | Enables debug mode. Set to `False` in production. |
| `DJANGO_ALLOWED_HOSTS` | `csv` | `localhost,127.0.0.1` | Comma-separated list of allowed host domains. |
| `EMAIL_USER` | `string` | `""` | SMTP email address for sending notifications. |
| `EMAIL_PASS` | `string` | `""` | SMTP password (use an App Password for Gmail). |

---

## Project Structure

```
Cloth-Management-System/
├── .env                        # Environment configuration
├── .gitignore                  # Git ignore rules
├── manage.py                   # Django CLI entry point
├── requirements.txt            # Python dependencies
├── db.sqlite3                  # SQLite database (auto-generated)
│
├── index/                      # Django project settings
│   ├── __init__.py
│   ├── settings.py             # Main Django settings
│   ├── urls.py                 # Root URL configuration
│   ├── wsgi.py                 # WSGI application (production)
│   └── asgi.py                 # ASGI application
│
├── app/                        # Main application
│   ├── __init__.py
│   ├── admin.py                # Django admin model registrations
│   ├── models.py               # Database models (Product, Category, Order, etc.)
│   ├── views.py                # View logic for all pages
│   ├── urls.py                 # App-level URL routing
│   ├── form.py                 # Form definitions
│   ├── context_processors.py   # Global template context data
│   ├── tests.py                # Unit tests
│   ├── apps.py                 # App configuration
│   ├── management/             # Custom management commands
│   ├── migrations/             # Database migration files
│   └── templatetags/           # Custom Django template tags
│
├── Templete/                   # HTML templates (Django templates)
│   ├── base.html               # Base template with common layout
│   ├── home1.html              # Landing page
│   ├── home.html               # Shop / product listing page
│   ├── product_detail.html     # Individual product page
│   ├── cart.html               # Shopping cart
│   ├── checkout.html           # Checkout page
│   ├── order.html              # Customer order history
│   ├── wishlist.html           # User wishlist
│   ├── login.html              # Login page
│   ├── signup.html             # Registration page
│   ├── dashboard.html          # Admin dashboard
│   ├── about.html              # About page
│   ├── contact.html            # Contact page
│   ├── addpro.html             # Add product (admin)
│   ├── editpro.html            # Edit product (admin)
│   ├── listpro.html            # List products (admin)
│   ├── addcat.html             # Add category (admin)
│   ├── editcat.html            # Edit category (admin)
│   ├── listcat.html            # List categories (admin)
│   └── ...                     # Additional templates
│
├── media/                      # User-uploaded media files
│   └── images/                 # Product images
│
└── middleware/                  # Custom middleware
    └── auth.py                 # Authentication middleware
```

---

## URL Routes

### Public Pages

| URL | View | Description |
|-----|------|-------------|
| `/` | `home1` | Landing page |
| `/shopping` | `home` | Shop page with search, filters, sorting, and pagination |
| `/about` | `about` | About page |
| `/contact` | `contact` | Contact page with form |
| `/product/<id>/` | `product_detail` | Product detail with ratings and reviews |

### Authentication

| URL | View | Description |
|-----|------|-------------|
| `/signup` | `signup` | Customer registration |
| `/login` | `login` | Unified login (customer + admin) |
| `/signout/` | `signout` | Logout and clear session |

### Cart & Checkout

| URL | View | Description |
|-----|------|-------------|
| `/cart/` | `cart` | View shopping cart |
| `/checkout` | `checkout` | Checkout page with order summary |
| `/update-cart-item/` | `update_cart_item` | AJAX: Update cart item quantity |
| `/remove-cart-item/` | `remove_cart_item` | AJAX: Remove item from cart |
| `/apply-coupon/` | `apply_coupon` | AJAX: Apply coupon code |

### Orders

| URL | View | Description |
|-----|------|-------------|
| `/order` | `order` | Customer order history |
| `/order/<id>/cancel/` | `cancel_order` | Cancel a pending order |
| `/order/<id>/edit/` | `edit_order` | Edit an order |
| `/update-order-status/` | `update_order_status` | AJAX: Update order status (admin) |
| `/export-orders-csv/` | `export_orders_csv` | Export orders to CSV |

### Wishlist & Ratings

| URL | View | Description |
|-----|------|-------------|
| `/wishlist/` | `view_wishlist` | View saved items |
| `/wishlist/add/<id>/` | `add_to_wishlist` | Add product to wishlist |
| `/wishlist/remove/<id>/` | `remove_from_wishlist` | Remove from wishlist |
| `/wishlist/toggle/<id>/` | `toggle_wishlist` | Toggle wishlist status |
| `/rating/submit/` | `submit_rating` | Submit product rating and review |

### Admin (Custom Panel)

| URL | View | Description |
|-----|------|-------------|
| `/admin-dashboard/` | `admin_dashboard` | Admin analytics dashboard |
| `/addcat` | `addcat` | Add category |
| `/edit/<id>/` | `editcat` | Edit category |
| `/del/<id>/` | `deletecat` | Delete category |
| `/listcat` | `listcat` | List all categories |
| `/addpro` | `addpro` | Add product |
| `/editpro/<id>/` | `editpro` | Edit product |
| `/deletepro/<id>/` | `deletepro` | Delete product |
| `/listpro` | `listpro` | List all products |
| `/newsletter/` | `newsletter_signup` | Newsletter subscriber management |

### Django Admin

| URL | Description |
|-----|-------------|
| `/admin/` | Django admin panel (Jet themed) — full CRUD for all models |

---

## Admin Panel

ERA provides **two admin interfaces**:

### 1. Django Admin (`/admin/`)

Access the powerful Django admin with the Jet Reboot theme. Log in with the superuser credentials you created during setup.

Features:
- Full CRUD operations on all models
- Filterable and searchable product lists
- Inline order management
- Coupon management
- Newsletter subscriber list
- Theme customization (6 color themes available)

### 2. Custom Admin Dashboard (`/admin-dashboard/`)

A purpose-built dashboard accessible by logging in with `admin@era.com`. Provides:

- Order overview and status management
- Inventory tracking
- Category and product management
- Quick actions for common admin tasks

---

## Database

### Default: SQLite

The project uses SQLite out of the box. The database file `db.sqlite3` is created automatically after running migrations.

### Switching to PostgreSQL (Production)

For production use, you may want to switch to PostgreSQL. Update `index/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}
```

Then add the corresponding variables to `.env` and install `psycopg2-binary`:

```bash
pip install psycopg2-binary
```

---

## Common Issues & Troubleshooting

### Migration Errors

If you encounter migration conflicts:

```bash
# Delete migration files (keep __init__.py)
# Then recreate and apply:
python manage.py makemigrations
python manage.py migrate --fake-initial
```

### Static/Media Files Not Loading

Ensure `DEBUG = True` in `.env` for development. For production:

```bash
python manage.py collectstatic
```

And configure your web server (Nginx/Apache) to serve `/media/` and `/static/` directories.

### Port Already in Use

```bash
# Use a different port
python manage.py runserver 8080
```

---

## Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes** and test thoroughly
4. **Commit** with a clear message: `git commit -m "Add: feature description"`
5. **Push** to your branch: `git push origin feature/your-feature-name`
6. **Open a Pull Request**

### Development Guidelines

- Follow [PEP 8](https://peps.python.org/pep-0008/) for Python code style
- Write meaningful commit messages
- Test your changes before submitting
- Update documentation if your changes affect user-facing features
- Ensure all migrations are included

### Reporting Bugs

If you find a bug, please open an issue with:

- A clear description of the problem
- Steps to reproduce
- Expected vs. actual behavior
- Your environment (OS, Python version, Django version)

---

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- Built with [Django](https://www.djangoproject.com/) — The web framework for perfectionists with deadlines
- Admin theme powered by [Django Jet Reboot](https://github.com/assem-ch/django-jet-reboot)
- UI components styled with [Bootstrap 5](https://getbootstrap.com/)
- Form handling via [Django Crispy Forms](https://django-crispy-forms.readthedocs.io/)

---

<p align="center">Made with ❤️ for the ERA Project</p>
