# Hospital Management System (HMS)

Full-stack **demo/teaching** application: **FastAPI** backend with layered architecture, **JWT** role-based access, **SQLite** (or PostgreSQL via URL), and a **vanilla HTML/CSS/JavaScript** frontend (no Bootstrap, no SPA framework).

> **Disclaimer:** This is **not** a certified medical or prod-ready healthcare system. Use for learning, seminars, and local development only.

---

## Table of contents

- [Features](#features)
- [Tech stack](#tech-stack)
- [Project layout](#project-layout)
- [Requirements](#requirements)
- [Quick start](#quick-start)
- [Configuration (`.env`)](#configuration-env)
- [Running the application](#running-the-application)
- [URLs](#urls)
- [Authentication & roles](#authentication--roles)
- [API overview](#api-overview)
- [Frontend](#frontend)
- [Database](#database)
- [Troubleshooting](#troubleshooting)
- [Development notes](#development-notes)

---

## Features

- **User authentication:** register (patient), login, JWT bearer tokens.
- **Roles:** `admin`, `doctor`, `patient`, `receptionist` — permissions enforced in services and routes.
- **Patient management:** CRUD (who can do what depends on role).
- **Doctor management:** create/list/update/delete (admin for full doctor lifecycle; doctors can update own profile).
- **Appointments:** booking with overlap checks (time window per doctor).
- **Medical records:** linked to patient, doctor, optional appointment.
- **Billing:** invoices with line items, totals, status (e.g. pending / paid).
- **Optional first-run admin seed** when the database has **zero** users.
- **OpenAPI:** interactive docs at `/docs`.

---

## Tech stack

| Layer | Technology |
|--------|------------|
| API | FastAPI |
| Validation / DTOs | Pydantic v2 |
| ORM | SQLAlchemy 2.x |
| DB (default) | SQLite (`hms.db`) |
| Password hashing | passlib + bcrypt (&lt; 4.1 for passlib compatibility) |
| Auth | JWT (python-jose), HTTP Bearer |
| Frontend | Static HTML, CSS, JS; token in `localStorage` |
| Config | pydantic-settings, `.env` |

---

## Project layout

```
fast/
├── README.md                 # this file
├── requirements.txt
├── .env.example              # copy to .env and edit
├── run.sh                    # run with system Python 3.10–3.13
├── run-uv.sh                 # run with Astral uv (downloads Python 3.13)
├── hms.db                    # SQLite DB (created at runtime; gitignored if listed)
├── app/
│   ├── main.py               # FastAPI app, CORS, static, lifespan, DB init
│   ├── core/
│   │   ├── config.py         # settings from environment
│   │   ├── security.py       # JWT, password hashing
│   │   └── deps.py           # get_current_user, require_roles
│   ├── db/
│   │   ├── base.py           # SQLAlchemy DeclarativeBase
│   │   └── session.py        # engine, SessionLocal
│   ├── models/               # ORM entities + enums
│   ├── schemas/              # Pydantic request/response models
│   ├── repositories/       # data access
│   ├── services/             # business rules
│   └── api/v1/routes/        # HTTP routers
└── static/
    ├── index.html            # login + patient registration
    ├── app.html              # dashboard (role-based UI)
    ├── css/app.css
    └── js/
        ├── api.js            # fetch + token helper (HmsApi)
        ├── login.js
        └── dashboard.js
```

Architecture flow: **Router → Service → Repository → DB**; Pydantic schemas at the boundary.

---

## Requirements

- **Python 3.10, 3.11, 3.12, or 3.13**  
  - **Python 3.14** is not supported yet: `pydantic-core` / PyO3 may fail to build.
- **pip** inside a **virtual environment** (recommended).
- Optional: **[uv](https://github.com/astral-sh/uv)** for installing CPython 3.13 when the OS only ships 3.14.

---

## Quick start

1. **Clone or copy** the project and `cd` into the project root (`fast/`).

2. **Create `.env`** from the example:
   ```bash
   cp .env.example .env
   ```
   Edit `.env`: set `SECRET_KEY` (e.g. `openssl rand -hex 32`), and optionally `ADMIN_SEED_EMAIL` / `ADMIN_SEED_PASSWORD`.

3. **Install dependencies** (using a venv):
   ```bash
   python3.13 -m venv .venv
   source .venv/bin/activate          # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Run** (pick one):
   ```bash
   ./run.sh          # prefers /usr/bin/python3.13, 3.12, …
   ```
   or, if your distro only has Python 3.14 for `python3`:
   ```bash
   # install uv once: https://docs.astral.sh/uv/
   ./run-uv.sh       # creates .venv with Python 3.13 via uv
   ```
   or manually:
   ```bash
   uvicorn app.main:app --reload
   ```

5. Open **http://127.0.0.1:8000** in a browser.

---

## Configuration (`.env`)

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | Default `sqlite:///./hms.db`. For PostgreSQL: e.g. `postgresql+psycopg2://user:pass@host:5432/dbname` |
| `SECRET_KEY` | Secret for signing JWTs — **must** be strong in any shared or deployed environment |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT lifetime (default `60`) |
| `ADMIN_SEED_EMAIL` | If set, and **no users exist** on startup, create this admin user |
| `ADMIN_SEED_PASSWORD` | Password for the seeded admin |
| `CORS_ORIGINS` | `*` for dev, or comma-separated origins for a separate frontend origin |

**Seeding:** the admin is created **only** when the user table is **empty**. If you already registered anyone, the seed will not run — use a fresh `hms.db` (delete the file) if you need a clean seeded admin.

Copy from **`.env.example`**; do not commit real secrets.

---

## Running the application

- **Backend + static files** are served by the same Uvicorn process.
- **Working directory** should be the project root so `sqlite:///./hms.db` resolves next to the app.

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

---

## URLs

| URL | Description |
|-----|-------------|
| `http://127.0.0.1:8000/` | Login & patient registration |
| `http://127.0.0.1:8000/app` | Dashboard (requires token) |
| `http://127.0.0.1:8000/docs` | Swagger UI (OpenAPI) |
| `http://127.0.0.1:8000/redoc` | ReDoc |
| `http://127.0.0.1:8000/api/v1/...` | JSON API base path |

---

## Authentication & roles

- **Login:** `POST /api/v1/auth/login` with JSON `{ "email", "password" }` → `{ "access_token", "token_type" }`.
- **Requests:** send `Authorization: Bearer <access_token>`.
- **Current user:** `GET /api/v1/auth/me` returns user fields plus optional `patient_id` / `doctor_id` for profile-linked accounts.

**Approximate capabilities (see service layer for exact rules):**

| Role | Typical access |
|------|----------------|
| **admin** | Full user/doctor/patient management, records, invoices, seed-style operations |
| **doctor** | Own profile, scoped appointments, create/view own-patient medical records as policy allows |
| **patient** | Own profile scope, book own appointments, own invoices |
| **receptionist** | Patients, appointments, invoices; not full admin |

---

## API overview

Base path: **`/api/v1`**.

| Area | Prefix | Notes |
|------|--------|--------|
| Auth | `/auth` | register patient, register receptionist (admin), login, me |
| Patients | `/patients` | CRUD with role checks |
| Doctors | `/doctors` | CRUD |
| Appointments | `/appointments` | List/create/update/delete (delete: admin/receptionist) |
| Medical records | `/medical-records` | List/create/update/delete (delete: admin) |
| Invoices | `/invoices` | List, create, `PATCH .../status` |

Full schemas and try-it-out calls: **`/docs`**.

---

## Frontend

- **Stack:** Plain HTML, CSS, JavaScript only.
- **Token:** Stored as `hms_token` in `localStorage` (demo only; not production-grade).
- **Flows:** `/` → login or register patient → `/app` dashboard with sidebar by role.
- **API:** Relative requests to `/api/v1` (same origin as the FastAPI server).

To test without the UI, use **Swagger** or any HTTP client with the same base URL and Bearer token.

---

## Database

- **Default file:** `hms.db` (SQLite) in the project directory.
- **Tables** are created on startup (`Base.metadata.create_all`) if they do not exist.
- **Persistence:** Successful API writes (users, patients, doctors, appointments, records, invoices) are stored in this database. JWTs are **not** stored server-side.
- **Reset:** Stop the app, delete `hms.db`, start again (and re-seed admin if desired).

For production you would typically use **PostgreSQL**, **Alembic** migrations, backups, and hardened auth (e.g. HTTP-only cookies, refresh tokens).

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'fastapi'`

Dependencies are not installed in the interpreter you use to run Uvicorn. Use a **venv** and `pip install -r requirements.txt`, or run **`./run-uv.sh`** / **`./run.sh`**.

### `externally-managed-environment` (pip on Arch / etc.)

Do not install into system Python. Use a venv and **`python -m pip`**, or **`./run-uv.sh`**.

### Python 3.14 / `pydantic-core` build failure

Use **Python 3.13 or lower**, or **`./run-uv.sh`** to install 3.13 via **uv**.

### Virtualenv `python` points to Cursor / wrong binary

Remove `.venv` and recreate with an explicit system interpreter, e.g.:

```bash
/usr/bin/python3.13 -m venv .venv
```

### `(trapped) error reading bcrypt version` / passlib

`requirements.txt` pins **`bcrypt>=4.0.1,<4.1`** for compatibility with **passlib 1.7.4**. Reinstall deps after changing `requirements.txt`.

### Admin login fails (“Invalid email or password”)

- The seeded admin exists **only** if the DB had **no users** on first startup with `ADMIN_SEED_*` set.
- If you registered other users first, or the DB was created with different credentials, either log in as an existing user or **delete `hms.db`** and restart (after backing up if needed).
- Password must match `.env` **exactly** (including `!` if used).

### `422` on login with `EmailStr` / `.local` domains

Login and several create bodies use plain **string** emails so dev domains work. If you still see strict email errors, ensure you are on the latest code paths (see `app/schemas`).

---

## Development notes

- **CORS:** Default `*` for local dev; tighten for real deployments.
- **Migrations:** Currently **no Alembic**; schema is created from models. For team production use, add Alembic.
- **Tests:** Add `pytest` + httpx `TestClient` as a next step.
- **Security:** Rotate `SECRET_KEY`, use HTTPS, never ship real patient data in demos without consent and legal review.

---

## License

No license file is included by default; add one if you distribute the project.
