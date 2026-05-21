# HMS — Full demo script (tomorrow-ready)

Use **one rehearsal** today: wipe DB → set `.env` seed → restart → walk this script once.

**Unified password for all demo users (easier typing on stage):**  
`HmsDemo2026!`

---

## A) Before demo (night before / 10 minutes early)

### 1. Fresh database so the seeded admin appears

Stop the server, then delete the SQLite file:

```bash
rm -f hms.db
```

(or move it aside if you ever need a backup.)

### 2. Put this in `.env` (credentials you will SAY on demo)

Important: **`ADMIN_SEED_EMAIL` / `ADMIN_SEED_PASSWORD` must exactly match what you click in the login form** for first login.

Suggested:

```env
ADMIN_SEED_EMAIL=admin@hms-demo.internal
ADMIN_SEED_PASSWORD=HmsDemo2026!
SECRET_KEY=<keep your existing secret or generate a new one>
```

(Rest of `.env` can stay default: `DATABASE_URL`, `CORS_ORIGINS`, etc.)

### 3. Start server

```bash
./run.sh
# or ./run-uv.sh
# or: uvicorn app.main:app --reload
```

### 4. Open browser tabs (optional)

- `http://127.0.0.1:8000/` — app  
- `http://127.0.0.1:8000/docs` — Swagger (backup if UI hiccups)

---

## B) Cheat sheet — all credentials you will show

Say these **out loud** while typing so judges remember one password rule: **everything uses `HmsDemo2026!`**.

| # | Role            | Email (login)                   | Password        | Created how |
|---|-----------------|----------------------------------|-----------------|-------------|
| 1 | **Admin**       | `admin@hms-demo.internal`        | `HmsDemo2026!`  | **Seed** (first server start after empty DB) |
| 2 | **Receptionist**| `riya.desk@mymail.internal`       | `HmsDemo2026!`  | Admin → Home → “Add receptionist” |
| 3 | **Doctor**      | `dr.sameer@mymail.internal`      | `HmsDemo2026!`  | Admin → Doctors → Add doctor |
| 4 | **Patient**     | `ananya.k@mymail.internal`      | `HmsDemo2026!`  | Admin → Patients → Add patient |

**Optional fifth user (shows public registration UI):**

| Role     | Email                      | Password        | Created how |
|----------|-----------------------------|-----------------|-------------|
| Patient  | `walkin.case@mymail.internal` | `HmsDemo2026!` | `/` → **Register (patient)** (do this **near the end** if you still have time) |

---

## C) Demo flow — scenes (recommended order)

### Scene 1 — Admin: seed login + create staff & patient (~4–5 min)

**Narrative:** *“Hospital starts with admin; admin onboards reception, doctor, and a registered patient.”*

1. Open **`/`** → **Sign in**.
   - Email: `admin@hms-demo.internal`  
   - Password: `HmsDemo2026!`

2. **Home** — point out: name, role `admin`, user id.

3. **Add receptionist** (same Home card):
   - Email: `riya.desk@mymail.internal`
   - Password: `HmsDemo2026!`
   - Full name: `Riya Nair (Reception)`

4. **Doctors** (sidebar):
   - Email: `dr.sameer@mymail.internal`
   - Password: `HmsDemo2026!`
   - Full name: `Dr. Sameer Kapoor`
   - Specialization: `General Physician`
   - License: `DEMO-KA-9042`
   - Department: `OPD`
   - **After save:** remember **Doctor id** from table (usually `1` if first doctor).

5. **Patients** (sidebar):
   - Email: `ananya.k@mymail.internal`
   - Password: `HmsDemo2026!`
   - Full name: `Ananya Krishnan`
   - Optionally DOB / phone for realism.
   - **After save:** remember **Patient id** from table (usually `1` if first staff-created patient).

**Write on paper:** `Patient id = ____` , `Doctor id = ____` (use real numbers from YOUR screen.)

---

### Scene 2 — Receptionist: appointments + billing (~3–4 min)

**Narrative:** *“Front desk schedules a visit and raises a bill.”*

1. **Sign out**.

2. **Sign in:**
   - `riya.desk@mymail.internal` / `HmsDemo2026!`

3. **Patients** — show list has Ananya.

4. **Appointments** — **New appointment:**
   - **Patient ID** = Ananya’s id  
   - **Doctor** = Dr. Sameer  
   - **Date/time** = **tomorrow** (or later today — avoid clashes with junk data)  
   - Reason e.g. `Follow-up consultation (demo)`

5. **Invoices** — **New invoice:**
   - Patient id = same  
   - Optional: link **Appointment ID** if you copied it from the appointments table row  
   - Due date (optional), description e.g. `OPD demo visit`  
   - At least **one line:** e.g. `Consultation` qty `1`, unit price `850` — add another line if you want (`Lab panel`, etc.)  
   - **Create**, then **Mark paid**.

**Talking point:** *“Appointment is scheduling; invoice is billing — both persisted in SQLite.”*

---

### Scene 3 — Doctor: view schedule + clinical record (~3 min)

**Narrative:** *“Doctor sees bookings and enters a medical record tied to patient (and optionally appointment).”*

1. **Sign out**.

2. **Sign in:** `dr.sameer@mymail.internal` / `HmsDemo2026!`

3. **Appointments** — confirm the receptionist’s booking appears.

4. **Medical records:**
   - **Patient ID** = Ananya’s id  
   - **Doctor ID** should mirror your login (often read-only auto-filled).  
   - Optional **Appointment ID** if visible from appointments screen.  
   - Diagnosis example: `Mild dehydration — clinically stable for demo.`  
   - Notes / prescription (short realistic text).

5. **Load** records with **Patient id** filter — show row appears.

---

### Scene 4 — Patient: own view (~2 min)

**Narrative:** *“Patient sees only their lifecycle: visits and bills.”*

1. **Sign out**.

2. **Sign in:** `ananya.k@mymail.internal` / `HmsDemo2026!`

3. **Home** — highlight **Patient id** returned from `/auth/me`.

4. **Appointments** — own list (scoped by backend).

5. **Invoices** — invoice total + status (**paid**) from reception demo.

---

### Scene 5 — Optional: Swagger + self-register (~1–2 min)

**Swagger:** Open `/docs` → **Authorize** with a copied JWT from Network tab or paste after login POST — prove **same API powers the SPA**.

**Self-register patient (shows public onboarding):**

1. **Sign out** completely.

2. On **`/`** → tab **Register (patient)**:
   - `walkin.case@mymail.internal` / `HmsDemo2026!`
   - Name etc.

3. Opens dashboard — show **different patient id** → **Appointment** dropdown still needs doctors in system (already created) → quick book slot.

If **short on time**, skip Scene 5 and only mention Register exists.

---

## D) Troubleshooting notes (during demo)

| Symptom | Quick fix |
|--------|-----------|
| Admin login fails | Wrong seed or DB not empty: `rm hms.db`, verify `.env` seed, restart. |
| Field “required” fails | Patient id / Doctor id typo — match table IDs. |
| Appointment 409 conflict | Same doctor overlapping window — choose another slot. |
| Doctor dropdown empty | You never completed Scene 1 doctor — go back as admin. |
| 403 on invoices as patient | Normal for **creating** invoices — reception/admin only. Patient **views**. |

---

## E) Optional card to print

```
HMS DEMO — ALL PASSWORDS: HmsDemo2026!

admin@hms-demo.internal          (ADMIN — from .env seed)
riya.desk@mymail.internal       (RECEPTION)
dr.sameer@mymail.internal        (DOCTOR)
ananya.k@mymail.internal         (PATIENT)

Flow: Admin → Reception → Doctor → Patient
Extra: "/" Register → walkin.case@mymail.internal
Backup: http://127.0.0.1:8000/docs
```

---

**Summary:** Forget old trials; **`rm hms.db`**, set seed to **`admin@hms-demo.internal`** + **`HmsDemo2026!`**, restart, then scenes **Admin → Reception → Doctor → Patient** touches **registration (staff-created users), login, appointments, records, invoices, role-based UI**.
