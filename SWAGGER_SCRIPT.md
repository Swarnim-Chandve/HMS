# HMS — Swagger Testing Script (Tomorrow-ready)

Use this when you want to **demo everything using Swagger `/docs` only** (no browser UI clicks).

## Demo prerequisites (do these once before the script)

### 0) Fresh start (so the seeded admin exists)
1. Stop the server (CTRL+C).
2. Delete SQLite DB:
   ```bash
   rm -f hms.db
   ```
3. Update `.env` seed so login works:
   ```env
   ADMIN_SEED_EMAIL=admin@hms-demo.internal
   ADMIN_SEED_PASSWORD=HmsDemo2026!
   ```
   Make sure your `.env` values match what you will type below.

### 1) Start server
```bash
./run.sh
# or ./run-uv.sh
```

### 2) Open Swagger
Open:
- `http://127.0.0.1:8000/docs`

---

## Credential values (use these consistently)

**One password for all demo users (easy on stage):**
`HmsDemo2026!`

### Seed admin (exists after step 0)
- **Admin email:** `admin@hms-demo.internal`
- **Admin password:** `HmsDemo2026!`

### Emails you will create (you can change names, but keep emails unique)
- **Receptionist email:** `riya.desk@mymail.internal`
- **Doctor email:** `dr.sameer@mymail.internal`
- **Patient email (registered via /auth/register/patient):** `ananya.k@mymail.internal`

### Another patient (created via admin /patients to test patient CRUD)
- **Patient email (admin-created):** `patient.crud@mymail.internal`

---

## Swagger token handling (important)

After each login, you will get an `access_token`. This token proves **who you are** (admin/doctor/patient/receptionist) for the next API calls.

### When you need the token
- **Only** after `POST /api/v1/auth/login` succeeds (HTTP 200) and returns JSON with `access_token`.
- Any protected endpoint (patients/doctors/appointments/records/invoices) needs the token in Swagger.

### Exactly how to use the token in Swagger
1. Call `POST /api/v1/auth/login`.
2. In the response JSON, copy the value of `access_token`.
3. In Swagger UI, click **Authorize** (top-right).
4. In the Bearer token field, paste:
   - `Bearer <PASTE_ACCESS_TOKEN>`
5. Click **Authorize**, then close the dialog.
6. Now execute protected endpoints — Swagger will automatically send the header:
   - `Authorization: Bearer <token>`

### Switching roles (Admin → Receptionist → Doctor → Patient)
Swagger can store **only one active Bearer token** at a time.

Whenever the script says “Login as X”:
1. Run the login request for that user.
2. Copy the new `access_token`.
3. Click **Authorize** again and paste the new token (it replaces the previous token).

### If you get 401/403 during the demo
- **401 Unauthorized**: token missing/expired/cleared → login again and re-authorize.
- **403 Forbidden**: you’re logged in as the wrong role → switch token by logging in as the right user and re-authorizing.

Then continue with the next endpoint calls in the script.

---

## Scene-by-scene Swagger flow (covers all features)

### Scene 1 — Login as Admin + create Doctor + create Receptionist + create Patient (3–5 min)

#### 1.1 Admin Login
`POST /api/v1/auth/login`

Request body:
```json
{
  "email": "admin@hms-demo.internal",
  "password": "HmsDemo2026!"
}
```

Response: `access_token`

After response:
- Note: keep `ADMIN_TOKEN`
- Click Swagger **Authorize**: `Bearer ADMIN_TOKEN`

#### 1.2 Create Doctor (Admin)
`POST /api/v1/doctors`

Request body:
```json
{
  "email": "dr.sameer@mymail.internal",
  "password": "HmsDemo2026!",
  "full_name": "Dr. Sameer Kapoor",
  "specialization": "General Physician",
  "license_number": "DEMO-KA-9042",
  "department": "OPD"
}
```

Response includes `id`
- Note: `DOCTOR_ID` from response

#### 1.3 Create Receptionist (Admin)
`POST /api/v1/auth/register/receptionist`

Request body:
```json
{
  "email": "riya.desk@mymail.internal",
  "password": "HmsDemo2026!",
  "full_name": "Riya Nair (Reception)"
}
```

Response includes `user_id`
- Note: `RECEPTIONIST_USER_ID` (not strictly required later, but good for debugging)

#### 1.4 Register a Patient (public endpoint)
`POST /api/v1/auth/register/patient`

Request body:
```json
{
  "email": "ananya.k@mymail.internal",
  "password": "HmsDemo2026!",
  "full_name": "Ananya Krishnan",
  "date_of_birth": "1995-06-15",
  "phone": "+1-555-0100",
  "address": "123 Test Street",
  "emergency_contact": "Friend +1-555-0199"
}
```

Response includes patient fields:
- Note: `PATIENT_ID` from response `id`

#### 1.5 Create another patient (to test patient CRUD)
`POST /api/v1/patients`

Request body:
```json
{
  "email": "patient.crud@mymail.internal",
  "password": "HmsDemo2026!",
  "full_name": "CRUD Patient",
  "date_of_birth": "2000-01-10",
  "phone": "+1-555-0200",
  "address": "456 Demo Ave",
  "emergency_contact": "N/A"
}
```

Response includes:
- Note: `CRUD_PATIENT_ID` from response `id`

---

### Scene 2 — Receptionist: Appointments + Billing (3–4 min)

#### 2.1 Receptionist Login
`POST /api/v1/auth/login`

Request body:
```json
{
  "email": "riya.desk@mymail.internal",
  "password": "HmsDemo2026!"
}
```

Response includes `access_token`
- Note: `RECEPTIONIST_TOKEN`
- Authorize: `Bearer RECEPTIONIST_TOKEN`

#### 2.2 Create Appointment
`POST /api/v1/appointments`

Use a future time. Example for “tomorrow” at 10:00 UTC:
```json
{
  "patient_id": 0,
  "doctor_id": 0,
  "scheduled_at": "2026-06-02T10:00:00Z",
  "reason": "Follow-up consultation (demo)"
}
```

Replace:
- `patient_id` = `PATIENT_ID`
- `doctor_id` = `DOCTOR_ID`

Response includes appointment `id`
- Note: `APPOINTMENT_ID`

#### 2.3 Create Invoice (with line items)
`POST /api/v1/invoices`

Request body:
```json
{
  "patient_id": 0,
  "appointment_id": 0,
  "due_date": "2026-06-15",
  "description": "OPD demo visit",
  "lines": [
    { "description": "Consultation", "quantity": 1, "unit_price": 850 },
    { "description": "Lab panel", "quantity": 1, "unit_price": 400 }
  ]
}
```

Replace:
- `patient_id` = `PATIENT_ID`
- `appointment_id` = `APPOINTMENT_ID`

Response includes:
- `amount_total` should equal 850 + 400 = **1250.00** (rounded per Decimal rules)
- Note: `INVOICE_ID`

#### 2.4 Mark Invoice Paid
`PATCH /api/v1/invoices/{invoice_id}/status`

Request body:
```json
{
  "status": "paid",
  "paid_at": "2026-06-01T10:05:00Z"
}
```

Use `{invoice_id}` = `INVOICE_ID`

Response:
- `status` becomes `paid`

---

### Scene 3 — Doctor: Create & list Medical Records (3 min)

#### 3.1 Doctor Login
`POST /api/v1/auth/login`

Request:
```json
{
  "email": "dr.sameer@mymail.internal",
  "password": "HmsDemo2026!"
}
```

Authorize with `Bearer DOCTOR_TOKEN`

#### 3.2 Create Medical Record
`POST /api/v1/medical-records`

Request body:
```json
{
  "patient_id": 0,
  "doctor_id": 0,
  "appointment_id": 0,
  "diagnosis": "Mild dehydration — clinically stable (demo)",
  "notes": "Advised oral hydration plan and follow-up advice.",
  "prescription": "Oral rehydration solution 250ml twice daily"
}
```

Replace:
- `patient_id` = `PATIENT_ID`
- `doctor_id` = `DOCTOR_ID`
- `appointment_id` = `APPOINTMENT_ID`

Response includes `record id`
- Note: `RECORD_ID`

#### 3.3 List Records (Doctor path)
`GET /api/v1/medical-records?patient_id=PATIENT_ID&limit=50`

Expected:
- response `items` contains the record

---

### Scene 4 — Patient: Own Appointments + Own Invoices (2 min)

#### 4.1 Patient Login
`POST /api/v1/auth/login`

Request:
```json
{
  "email": "ananya.k@mymail.internal",
  "password": "HmsDemo2026!"
}
```

Authorize with `Bearer PATIENT_TOKEN`

#### 4.2 Get own appointments (scoped)
`GET /api/v1/appointments?limit=50`

Expected:
- `items[].patient_id` matches `PATIENT_ID`

#### 4.3 Get own invoices (scoped)
`GET /api/v1/invoices?limit=50`

Expected:
- `items[].patient_id` matches `PATIENT_ID`
- status should show **paid**

---

### Scene 5 — Patient Management CRUD (Admin) (2–3 min)

#### 5.1 Login back as Admin
`POST /api/v1/auth/login` (same body as Scene 1.1)

Authorize: `Bearer ADMIN_TOKEN`

#### 5.2 List patients
`GET /api/v1/patients?limit=20`

Expected: includes `CRUD_PATIENT_ID`

#### 5.3 Update patient
`PATCH /api/v1/patients/{patient_id}`

Replace `{patient_id}` = `CRUD_PATIENT_ID`

Request body:
```json
{
  "phone": "+1-555-0999",
  "address": "Updated demo address"
}
```

Expected: response shows updated fields

#### 5.4 Delete patient
`DELETE /api/v1/patients/{patient_id}`

Use `{patient_id}` = `CRUD_PATIENT_ID`

Expected:
- code `204 No Content`

---

### Scene 6 — Doctor Update & Appointment Update (optional but nice) (1–2 min)

#### 6.1 Update appointment status
`PATCH /api/v1/appointments/{appointment_id}`

Use `{appointment_id}` = `APPOINTMENT_ID`

Request body:
```json
{
  "status": "completed",
  "reason": "Completed demo visit"
}
```

#### 6.2 Update doctor profile (Admin)
`PATCH /api/v1/doctors/{doctor_id}`

Use `{doctor_id}` = `DOCTOR_ID`

Request body:
```json
{
  "specialization": "General Medicine (Updated)",
  "department": "OPD (Updated)"
}
```

---

## Final verification calls (quick)

1. `GET /api/v1/auth/me` (check `role`)
2. `GET /api/v1/appointments?limit=50` (as receptionist/admin)
3. `GET /api/v1/invoices?limit=50` (as patient; verify `paid`)
4. `GET /api/v1/medical-records?patient_id=<PATIENT_ID>&limit=50` (as doctor)

---

## Common demo failures (fast fixes)

- **401 / “Invalid email or password”**:
  - Admin seed did not run (DB not empty) OR you changed `.env` but didn’t delete `hms.db`.
  - Ensure `.env` seed email+password match exactly.
- **403**:
  - You’re using wrong role for that endpoint. Switch token.
- **409 conflict** on appointment:
  - The doctor already has an appointment overlapping the scheduling window.
  - Choose a different future time.
- **422 validation**:
  - IDs are wrong (use response `id` values, not guesses).
  - `scheduled_at` must be a valid ISO datetime string.

