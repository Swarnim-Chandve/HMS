# Manual testing guide — HMS

Use this to verify each feature with the **web UI** and/or **Swagger** (`http://127.0.0.1:8000/docs`).  
**Prerequisites:** server running; you know what is in your **`.env`** (especially `ADMIN_SEED_*`).

**Credentials naming in this guide**

- **Admin (seeded):** Use `ADMIN_SEED_EMAIL` and `ADMIN_SEED_PASSWORD` from `.env`.  
  Example values used below: **`admin@example.com`** / **`ChangeMeAfterFirstLogin1!`** — **replace with your actual `.env` values.**
- **Seeding rule:** The admin user is created **only when the database has zero users** on first application startup. If you already have users, either log in as an existing user or **delete `hms.db`** (after backup) and restart with desired `ADMIN_SEED_*` in `.env`.
- All other emails/passwords in this guide are **examples**; you can change them as long as passwords are **8+ characters** where registration requires it.

---

## 0) Global checks (before feature tests)

| Step | Action | How you know it works |
|------|--------|------------------------|
| 0.1 | Open `http://127.0.0.1:8000/docs` | Swagger UI loads; tag list shows auth, patients, doctors, etc. |
| 0.2 | Open `http://127.0.0.1:8000/` | Login page loads; link to Dashboard / API docs works. |
| 0.3 | Open `http://127.0.0.1:8000/app` **without** logging in | You are redirected to `/` or login fails — protected route is enforced. |

---

## 1) Authentication — login (admin)

**Goal:** JWT is issued and `/auth/me` returns the admin user.

| Step | Action | Expected result |
|------|--------|-----------------|
| 1.1 | Go to `/`, enter admin email + password from `.env`, click **Sign in**. | Redirect to `/app` (dashboard). |
| 1.2 | On dashboard **Home**, read the card. | Shows your **email**, **role: admin**, **user id**. `patient_id` / `doctor_id` are usually empty for a pure admin. |
| 1.3 | In Swagger: **POST** `/api/v1/auth/login` with same JSON body, then **GET** `/api/v1/auth/me` with **Authorize** (Bearer token). | `200` + body includes `"role": "admin"`. |

**Failure:** “Invalid email or password” → wrong password, wrong email, or **no admin row** (DB was not empty on first seed). Fix: confirm `.env` matches what you type, or reset DB and restart so seed runs.

---

## 2) Authentication — register patient + auto-login

**Goal:** New patient user exists; token works; `patient_id` appears on `/me`.

| Step | Action | Expected result |
|------|--------|-----------------|
| 2.1 | Sign out (dashboard) or clear site data. Go to `/`, tab **Register (patient)**. | Form visible. |
| 2.2 | Use a **new** email, e.g. `patient-a@test.local`, password `TestPass1234`, fill name, optional fields, submit. | Redirect to `/app`. |
| 2.3 | **Home** block. | **role: patient**; **patient_id** is a number (e.g. `1`). |
| 2.4 | Swagger: register then login, **GET** `/auth/me`. | `patient_id` present, `role` is `patient`. |

---

## 3) Authentication — sign out + token behavior

| Step | Action | Expected result |
|------|--------|-----------------|
| 3.1 | On `/app`, click **Sign out**. | Back to `/` or home; token cleared. |
| 3.2 | Manually open `/app` again. | Redirected or empty state that forces login (implementation: redirect to `/`). |
| 3.3 | Sign in again. | Dashboard loads again. |

---

## 4) Admin — create doctor

**Goal:** Doctor user + doctor profile row; list API and UI show the doctor.

**Prerequisites:** Logged in as **admin**.

| Step | Action | Expected result |
|------|--------|-----------------|
| 4.1 | Dashboard → **Doctors** → **Add doctor**. | Form: email, password, name, specialization, license, department. |
| 4.2 | Example: `doctor1@test.local`, `TestPass1234`, name `Dr. Demo One`, specialization `General`, license `LIC-001`, department `OPD`. Submit. | Toast / no error; table lists new row with **id**, name, email. |
| 4.3 | Swagger: **POST** `/api/v1/doctors` with Bearer (admin), then **GET** `/api/v1/doctors`. | `201` then `200` with `items` containing the doctor. |

**Failure:** `403` → not admin. `409` → email already exists.

---

## 5) Admin — register receptionist

**Goal:** Second staff role can log in and use allowed modules.

| Step | Action | Expected result |
|------|--------|-----------------|
| 5.1 | As **admin**, dashboard **Home** → **Add receptionist** section. | Fields: email, password, full name. |
| 5.2 | Example: `desk1@test.local`, `TestPass1234`, name `Front Desk`. Submit. | Success message / no error. |
| 5.3 | Sign out; sign in as `desk1@test.local` / `TestPass1234`. | **role: receptionist** on Home. |
| 5.4 | Check sidebar: **Patients**, **Appointments**, **Invoices** available; **Doctors** create may be hidden (receptionist cannot create doctors). | Matches your UI rules. |

---

## 6) Patients — list and create (admin or receptionist)

**Goal:** Patient records and linked user accounts.

**Prerequisites:** **admin** or **receptionist**.

| Step | Action | Expected result |
|------|--------|-----------------|
| 6.1 | **Patients** → **Add patient**: new email `patient-b@test.local`, password `TestPass1234`, name, optional DOB/phone/address. Submit. | Row in table with **id** (note this as **patient_id** for appointments). |
| 6.2 | **GET** `/api/v1/patients` in Swagger (with staff token). | JSON `items` includes the new patient. |

**Doctor role:** Can often **list** patients (policy in your app); **create** patient is for admin/receptionist in the UI form.

---

## 7) Appointments — create and list

**Goal:** Appointment row links `patient_id`, `doctor_id`, time, status.

**Prerequisites:** At least one **doctor** (§4) and one **patient id** (§2 or §6).

| Step | Action | Expected result |
|------|--------|-----------------|
| 7.1 | As **admin** or **receptionist**, **Appointments** → **New appointment**: set **Patient ID** (integer from Patients table), choose **Doctor** from dropdown, pick a **future** date/time (datetime-local), optional reason. Submit. | New row in appointments table: ids, `scheduled_at`, `status` (e.g. `scheduled`). |
| 7.2 | Try two bookings for the **same doctor** at the **same** or **very close** times. | Second may return **409** (conflict) — overlap rule. |
| 7.3 | As **patient** (from §2): **Appointments** → book: patient id should be **fixed/readonly** to your `patient_id`; pick doctor + time. Submit. | Row appears; scoped list shows your appointments. |

---

## 8) Medical records — create and list

**Goal:** Record tied to patient, doctor, optional appointment.

**Prerequisites:** **Admin** or **doctor** token. Know **patient_id**, **doctor_id** (from Doctors list or seed).

| Step | Action | Expected result |
|------|--------|-----------------|
| 8.1 | As **doctor** (log in as `doctor1@test.local`): **Records** → **Doctor ID** field may be **readonly** with your id. Enter **Patient ID**, optional **Appointment ID**, diagnosis/notes/prescription. Submit. | Success toast; table can be loaded with **Load** after entering **Patient ID** in filter (doctor must filter by patient). |
| 8.2 | As **admin**: **Load** with **empty** patient filter (if UI allows) → recent records for all patients, or enter a **patient id** → records for that patient. | Table rows with record id, patient, doctor, diagnosis, time. |
| 8.3 | Swagger: **POST** `/api/v1/medical-records` with valid body. | `201` and record appears in **GET** list. |

**Receptionist:** Typically **no** access to create clinical records (403) — confirm in your policy.

---

## 9) Billing — create invoice, mark paid

**Goal:** Invoice with lines, total, status update.

**Prerequisites:** **admin** or **receptionist**. A **patient_id**; optional **appointment_id**.

| Step | Action | Expected result |
|------|--------|-----------------|
| 9.1 | **Invoices** → fill **Patient ID**, optional **Appointment ID**, due date, description, at least one **line** (description + qty + unit price). Submit. | New row: **Total** matches sum of lines; **status** `pending`. |
| 9.2 | Click **Mark paid** (if shown for pending). | Status becomes **paid** (or equivalent). |
| 9.3 | As **patient** (login as patient user): **Invoices** tab. | See **own** invoices only. |
| 9.4 | Swagger: **PATCH** `/api/v1/invoices/{id}/status` with `{"status":"paid"}`. | `200` and `paid_at` set. |

---

## 10) Doctor — update own profile (optional API check)

| Step | Action | Expected result |
|------|--------|-----------------|
| 10.1 | Log in as doctor. **PATCH** `/api/v1/doctors/{doctor_id}` (Swagger) with own id, new `full_name` or `specialization`. | `200`; **GET** doctor reflects change. |

---

## 11) Admin — delete patient (destructive)

**Warning:** Removes linked user cascade per your ORM rules; use a **test** patient only.

| Step | Action | Expected result |
|------|--------|-----------------|
| 11.1 | Swagger: **DELETE** `/api/v1/patients/{id}` as admin. | `204`; patient disappears from **GET** list. |

---

## 12) Persistence (database)

| Step | Action | Expected result |
|------|--------|-----------------|
| 12.1 | Create at least one appointment and one invoice. **Stop** the server. | — |
| 12.2 | **Start** the server again; log in; open lists. | Data still there → stored in **`hms.db`** (SQLite default). |

---

## 13) Quick credential matrix (examples)

| Role | Example email | Example password | Notes |
|------|----------------|------------------|--------|
| Admin (seed) | From `.env` `ADMIN_SEED_EMAIL` | From `.env` `ADMIN_SEED_PASSWORD` | Only if DB was empty on first run with seed set |
| Patient | `patient-a@test.local` | `TestPass1234` | Via Register on `/` |
| Doctor | `doctor1@test.local` | `TestPass1234` | Created by admin in Doctors form |
| Receptionist | `desk1@test.local` | `TestPass1234` | Created by admin on Home |

Replace with your real values; keep passwords **8+ characters** for registration endpoints.

---

## 14) Checklist summary

- [ ] Swagger loads; API base responds.  
- [ ] Login as admin; `/app` shows admin; `/me` returns `role: admin`.  
- [ ] Register patient; `patient_id` on `/me`.  
- [ ] Sign out; `/app` requires login again.  
- [ ] Create doctor; appears in list.  
- [ ] Create receptionist; can log in as receptionist.  
- [ ] Create patient (staff); appears in list.  
- [ ] Create appointment; appears in list; conflict rule test (optional).  
- [ ] Create medical record as doctor/admin; list loads.  
- [ ] Create invoice; mark paid; patient sees own invoices.  
- [ ] Restart server; data persists.  

If any step fails, note **HTTP status**, **response body** (`detail` / `errors`), and **which role** you used — then compare with `README.md` troubleshooting and service-layer rules in the codebase.
