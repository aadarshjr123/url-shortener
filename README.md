# 🚀 URL Shortener --- Because Long URLs Deserve a Break

Welcome to my full-stack URL Shortener project --- a clean,
production-style backend powered by FastAPI and a modern React + Vite
frontend.

Yes, it shortens URLs.\
But more importantly, it demonstrates architecture, scalability
thinking, and real-world backend practices.

------------------------------------------------------------------------

## 🧠 Why This Project Exists

Because:

-   Long URLs are ugly.
-   Clean architecture is beautiful.

This project focuses on: - Proper backend structure - Database
migrations - Service layers - Clean frontend architecture - Dockerized
environment - Real-world production patterns

------------------------------------------------------------------------

## 🏗️ Architecture Overview

    Frontend (React + Vite)
            ↓
    Backend (FastAPI + Gunicorn)
            ↓
    PostgreSQL
            ↓
    Redis (Caching layer)

Everything runs inside Docker like a civilized engineer.

------------------------------------------------------------------------

## 🛠️ Tech Stack

### Backend

-   FastAPI
-   SQLAlchemy
-   Alembic (Database migrations)
-   PostgreSQL
-   Redis
-   Gunicorn + Uvicorn
-   Docker

### Frontend

-   React
-   TypeScript
-   Vite
-   Axios (API layer separation)

------------------------------------------------------------------------

## 📂 Project Structure (Clean & Scalable)

### Backend

    app/
     ├── api/
     ├── services/
     ├── repositories/
     ├── schemas/
     ├── db/
     ├── core/
     └── main.py

No spaghetti. Only layered architecture.

### Frontend

    src/
     ├── api/
     ├── services/
     ├── pages/
     ├── types/
     └── App.tsx

Because scalable apps don't live inside `App.tsx`.

------------------------------------------------------------------------

## ⚡ How To Run

### 1️⃣ Start Backend (Docker)

``` bash
docker-compose up --build
```

Backend runs at:

    http://localhost:8080

Swagger docs:

    http://localhost:8080/docs

------------------------------------------------------------------------

Frontend runs at:

    http://localhost:3000

------------------------------------------------------------------------

## 🧪 Features

-   🔗 Shorten long URLs
-   🗃️ Store URLs in PostgreSQL
-   ⚡ Redis caching support
-   🧱 Clean service/repository architecture
-   🔄 Alembic migrations
-   🐳 Fully Dockerized
-   📦 Production-style backend boot with Gunicorn

------------------------------------------------------------------------

## 🚧 What I Would Improve Next

If this were production:

-   Add structured logging
-   Add health checks & monitoring
-   Add CI/CD pipeline
-   Add unit & integration tests

------------------------------------------------------------------------

## 💬 Final Note

This project might shorten URLs.

But more importantly --- it demonstrates that I don't shorten
engineering quality.

