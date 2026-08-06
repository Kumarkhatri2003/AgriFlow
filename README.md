# 🌾 AgriFlow — Digital Agriculture Platform

AgriFlow is a digital agriculture and farm management platform designed for the Nepalese context (covering Hilly, Himalayan, and Terai regions). It supports crop lifecycle management, livestock tracking, financial ledgers, local weather integration, and smart notifications for farmers.

## 📂 Project Structure

This repository is split into two main components:

1. **[`backend/`](file:///c:/Users/DELL/Projects/AgriFlow/backend)**:
   * A Django and Django REST Framework (DRF) REST API.
   * Handles user authentication, database operations, cron scheduling via APScheduler, and weather integrations.
   * Read the [Backend README](file:///c:/Users/DELL/Projects/AgriFlow/backend/README.md) for local setup, testing, and Render deployment configurations.

2. **[`frontend/`](file:///c:/Users/DELL/Projects/AgriFlow/frontend)**:
   * The web application interface for farmers and admins (to be fully integrated).
   * Read the [Frontend README](file:///c:/Users/DELL/Projects/AgriFlow/frontend/README.md) for setup details.

---

## 🛠️ Main Tech Stack

* **Backend:** Python (Django & DRF), PostgreSQL, JWT, APScheduler, OpenAPI 3.0 (Swagger)
* **Frontend:** React / Vite (HTML, Vanilla CSS)

---

## 🚀 Getting Started

To get the backend application running locally:
1. Navigate to the `backend/` directory.
2. Follow the detailed steps in the [Backend README](file:///c:/Users/DELL/Projects/AgriFlow/backend/README.md) to install dependencies, configure environment settings, run database migrations, and launch the server.