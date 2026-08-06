# 🌾 AgriFlow — Backend API Service

AgriFlow is a modern digital agriculture and farm management platform specifically tailored to the geographical, linguistic, and agricultural context of Nepal (covering Himalayan, Hilly, and Terai regions). 

This repository contains the backend codebase—a robust, high-performance REST API built using **Django** and **Django REST Framework (DRF)**.

---

## 🚀 Key Features

* **🔑 JWT Authentication:** Secure registration and login for farmers and admins using simplejwt, featuring token rotation and blacklist support.
* **🌱 Crop Life-Cycle Management:** Tracking planting dates, active crop varieties, and Nepal-specific geographical growth stages.
* **🐄 Livestock & Breeding Management:** Tracking animal details, vaccination logs, pregnancy stages, and health follow-ups.
* **💰 Financial Ledger:** Dedicated tracker for incomes, expenses, and crop-level profit margin analysis.
* **⏰ Escalating Notification Engine:** 
  * Automatics signals on crop/livestock CRUD actions.
  * On-demand daily checkups when farmers access the app.
  * Automated cron-like background jobs firing at **04:00 AM** to generate reminders.
* **🌦️ Weather Caching:** Weather API integration with local memory caching (`LocMemCache`) to minimize third-party API usage.
* **📖 OpenAPI Documentation:** Auto-generated API specs with Swagger UI and ReDoc using `drf-spectacular`.

---

## 🛠️ Technology Stack

* **Framework:** Django 6.0.2 & Django REST Framework (DRF)
* **Authentication:** JWT via `djangorestframework-simplejwt`
* **Scheduler:** `django-apscheduler` & `APScheduler`
* **Database:** PostgreSQL (with `psycopg2-binary`)
* **Documentation:** `drf-spectacular` & `drf-yasg` (OpenAPI 3.0)
* **Environment Configuration:** `python-dotenv`

---

## 📦 Local Installation & Setup

### 1. Prerequisites
* Python 3.10+ installed
* PostgreSQL database server running locally

### 2. Clone and Setup Environment
Navigate to the backend directory:
```bash
cd backend
```

Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Environment Settings
Create a `.env` file by copying the template:
```bash
cp .env.example .env
```
Open `.env` and fill in your local PostgreSQL credentials, Gmail SMTP App Passwords, and API keys.

### 4. Database Setup & Migrations
Create your local PostgreSQL database (e.g., `agriflow_db`), and run the migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Running the Application
Start the Django development server:
```bash
python manage.py runserver
```
* The API will be available at: `http://127.0.0.1:8000/`
* The interactive API docs (Swagger) will be available at: `http://127.0.0.1:8000/api/schema/docs/`

---

## 🧪 Testing & Quality Assurance

To execute the test suite containing automated unit tests for authorization, notification triggers, financial metrics, and validator rules, run:
```bash
python manage.py test
```

---

## 🌐 Production Deployment (Render)

This project is configured to run out-of-the-box on platforms like **Render**.

### 1. Required Render Environment Variables
Add the following keys in your Render Web Service dashboard under the **Environment** tab:

| Key | Example Value | Description |
| :--- | :--- | :--- |
| `SECRET_KEY` | `your-secure-production-key` | Long random security token. |
| `DEBUG` | `False` | Turn off developer details in production. |
| `ALLOWED_HOSTS` | `agriflow-api.onrender.com` | Render domain url. |
| `DB_NAME` | `agriflow_production` | PostgreSQL database name. |
| `DB_USER` | `postgres` | Database username. |
| `DB_PASSWORD` | `your-db-password` | Database password. |
| `DB_HOST` | `dpg-xxxx.render.com` | Remote database host link. |
| `DB_PORT` | `5432` | Postgres port. |
| `EMAIL_HOST_USER` | `official.agriflow@gmail.com` | Sender Gmail address. |
| `EMAIL_HOST_PASSWORD` | `xxxx xxxx xxxx xxxx` | Secure 16-character Gmail App Password. |
| `WEATHER_API_KEY` | `your-weather-api-key` | Token for external weather API. |
| `CORS_ALLOW_ALL_ORIGINS` | `False` | Lock down API queries to trusted sources. |
| `CORS_ALLOWED_ORIGINS` | `https://agriflow.onrender.com` | Your deployed frontend URL. |
| `FRONTEND_URL` | `https://agriflow.onrender.com` | Integration link for app redirects. |

### 2. Render Build & Start Commands
* **Build Command:**
  ```bash
  pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
  ```
* **Start Command:**
  ```bash
  gunicorn config.wsgi:application
  ```
