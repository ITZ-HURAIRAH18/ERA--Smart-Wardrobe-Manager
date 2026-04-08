# ERA - Limitless Fashion

A modern Django 5.1 fashion e-commerce platform with a premium design system.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip

### Local Development Setup

```bash
# 1. Clone and navigate to project
cd Cloth-Management-System

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment (optional - .env already exists)
# Edit .env file with your settings

# 5. Run migrations
python manage.py migrate

# 6. Create admin user (optional - for Django admin)
python manage.py createsuperuser

# 7. Create default categories (optional)
python manage.py shell
>>> from app.models import Cat
>>> Cat.objects.bulk_create([Cat(name='Men'), Cat(name='Women'), Cat(name='Children')])
>>> exit()

# 8. Run development server
python manage.py runserver
```

Visit: `http://127.0.0.1:8000`

### Demo Credentials
- **Admin**: admin@era.com / admin123
- **Customer**: Sign up via `/signup`

## 📁 Project Structure

```
Cloth-Management-System/
├── .env                    # Environment configuration
├── .gitignore
├── manage.py
├── requirements.txt
├── vercel.json             # Vercel deployment config
├── build.sh                # Vercel build script
├── db.sqlite3              # SQLite database
│
├── index/                  # Django project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── app/                    # Main application
│   ├── models.py           # Customer, Product, Category, Order, etc.
│   ├── views.py            # All view logic
│   ├── urls.py             # URL routing
│   ├── form.py             # Django forms
│   ├── context_processors.py
│   ├── templatetags/       # Custom template filters
│   │   └── cart.py
│   └── migrations/
│
├── Templete/               # HTML templates (note: intentional spelling)
│   ├── base.html           # Base template with ERA design system
│   ├── home1.html          # Landing page (7 animated sections)
│   ├── home.html           # Shopping page with sticky sidebar
│   ├── cart.html           # Cart with AJAX updates
│   ├── checkout.html       # Multi-step checkout
│   ├── login.html          # 100vh split layout
│   ├── signup.html         # 100vh split layout
│   ├── order.html          # Customer orders timeline
│   ├── wishlist.html
│   ├── about.html
│   ├── contact.html
│   ├── dashboard.html      # Admin dashboard with Chart.js
│   ├── addpro.html         # Add product form
│   ├── editpro.html        # Edit product form
│   ├── listpro.html        # Products list table
│   ├── addcat.html         # Add category form
│   ├── editcat.html        # Edit category form
│   ├── listcat.html        # Categories list table
│   └── orderadmin.html     # Admin orders management
│
├── media/                  # Uploaded files
│   └── images/
└── middleware/
    └── auth.py
```

## 🎨 Design System

### Color Palette
| Color | Hex | Usage |
|-------|-----|-------|
| ERA Black | `#0D0D0D` | Primary dark backgrounds |
| ERA Navy | `#1a1a2e` | Navbar, footers, headings |
| ERA Gold | `#C9A96E` | Primary accent, buttons, links |
| ERA Gold Dark | `#A8844A` | Hover states |
| ERA White | `#FFFFFF` | Backgrounds |
| ERA Cream | `#FAF8F5` | Secondary backgrounds |
| ERA Stone | `#F2EDE6` | Tertiary backgrounds |
| ERA Muted | `#8A8178` | Secondary text |
| ERA Border | `#E8E2D9` | Borders, dividers |
| ERA Text | `#2C2825` | Primary text |
| ERA Success | `#2D6A4F` | Success states |
| ERA Warning | `#B7791F` | Warning states |
| ERA Danger | `#9B2335` | Error states |

### Typography
- **Headings**: Cormorant Garamond (weights: 300, 400, 600, 700)
- **Body**: DM Sans (weights: 300, 400, 500)
- **Loaded via**: Google Fonts CDN

### Spacing
- Section padding: `100px 0` desktop, `60px 0` tablet, `40px 0` mobile
- Container: `max-width: 1200px`, padding `0 24px`
- Border-radius: `2px` buttons, `8px` cards, `16px` images, `50px` pills

### Animation
- Easing: `cubic-bezier(0.25, 0.46, 0.45, 0.94)`
- Hover: `0.35s`, Enter: `0.7s`, Stagger: `0.08s`

## 📄 Pages

### Customer Pages
1. **Landing** (`/`) — Hero, stats, categories, featured products, trust badges, testimonials, CTA
2. **Shop** (`/shopping`) — Product grid with sticky filter sidebar, search, sort, pagination
3. **Product Detail** (`/product/<id>/`) — Full product page with ratings, reviews, related products
4. **Cart** (`/cart/`) — Split layout with AJAX quantity updates
5. **Checkout** (`/checkout`) — Multi-step: shipping → review → confirm
6. **Orders** (`/order`) — Customer order history with timeline and tracking
7. **Wishlist** (`/wishlist/`) — Saved products grid
8. **Profile** (`/profile/`) — Account management
9. **About** (`/about`) — Company story and values
10. **Contact** (`/contact`) — Contact form, map, FAQ

### Authentication
- **Login** (`/login`) — 100vh split layout with image
- **Signup** (`/signup`) — 100vh split layout with password strength

### Admin Pages
- **Dashboard** (`/admin-dashboard/`) — Stats, charts (Chart.js), recent orders, low stock alerts
- **Add Product** (`/addpro`) — Professional form with image upload
- **Edit Product** (`/editpro/<id>/`) — Same as add with pre-filled data
- **Products List** (`/listpro`) — Searchable table with edit/delete actions
- **Add Category** (`/addcat`) — Simple form
- **Edit Category** (`/edit/<id>/`) — Simple form
- **Categories List** (`/listcat`) — Table with actions
- **Orders Management** (`/finalorder`) — Filterable table with status updates

## 🔧 Features

### Core
- Session-based shopping cart
- AJAX cart updates (quantity change, remove)
- Multi-step checkout with coupon support
- Product ratings and reviews
- Wishlist with AJAX toggle
- Order tracking with timeline
- Newsletter subscription
- Contact form

### Admin
- Sales dashboard with Chart.js graphs
- Revenue overview (line chart)
- Order status breakdown (doughnut chart)
- Low stock alerts
- CSV export for orders
- Inline status updates via AJAX

### Design
- Announcement bar with sessionStorage persistence
- Sticky navbar with scroll transform
- Scroll-triggered animations
- Toast notifications for Django messages
- Responsive mobile-first design
- Bootstrap 5.3 (CDN only — no build step)

## 🚀 Vercel Deployment

### 1. Prepare for Deployment
```bash
# Make sure your .env has production values:
DJANGO_DEBUG=false
DJANGO_SECRET_KEY=<your-secure-key>
DJANGO_ALLOWED_HOSTS=your-app.vercel.app,localhost
```

### 2. Deploy to Vercel
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Production deploy
vercel --prod
```

### 3. Post-Deployment
- Run migrations in Vercel shell: `vercel shell` → `python manage.py migrate`
- Create superuser: `python manage.py createsuperuser`
- Set environment variables in Vercel dashboard

### Environment Variables for Vercel
| Variable | Value |
|----------|-------|
| `DJANGO_SECRET_KEY` | Generate with: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DJANGO_DEBUG` | `false` |
| `DJANGO_ALLOWED_HOSTS` | `.vercel.app,.now.sh` |
| `VERCEL` | `true` |
| `EMAIL_USER` | Your Gmail |
| `EMAIL_PASS` | Your app password |

## 🛠️ Tech Stack

- **Backend**: Django 5.1.4, Python 3.11
- **Database**: SQLite (dev) → PostgreSQL (production recommended)
- **Frontend**: Bootstrap 5.3 (CDN), Vanilla JS
- **Fonts**: Google Fonts (Cormorant Garamond + DM Sans)
- **Charts**: Chart.js 4.x
- **Deployment**: Vercel
- **Static Files**: WhiteNoise

## 📝 Notes

- Template folder is named `Templete/` (intentional spelling — configured in settings)
- Media files (uploads) are stored in `/media/images/`
- No npm/webpack — Bootstrap loaded via CDN only
- All CSS is inline in templates
- All JavaScript is vanilla (no frameworks)

## 🔐 Security

- Passwords stored in plaintext (Customer model — upgrade to bcrypt for production)
- CSRF protection enabled on all forms
- Session-based authentication
- Admin access restricted by email check (`admin@era.com`) or Django `is_staff`

## 📧 Support

For issues or questions, check the code comments which include bug fix references, or reach out to the development team.

---

**ERA Fashion** — Limitless fashion at your fingertips.
