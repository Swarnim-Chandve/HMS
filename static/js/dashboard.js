/* HMS dashboard — role-based */
(function () {
  var api = HmsApi.api;
  if (!HmsApi.getToken()) {
    location.href = "/";
    return;
  }

  var me = null;
  var currentView = "home";

  function toast(msg, isErr) {
    var el = document.getElementById("toast");
    if (!el) return;
    el.textContent = msg;
    el.className = (isErr ? "error" : "ok") + " show";
    el.style.display = "block";
    setTimeout(function () {
      el.className = "";
      el.style.display = "none";
    }, 4500);
  }

  function esc(s) {
    if (s == null) return "";
    var d = document.createElement("div");
    d.textContent = String(s);
    return d.innerHTML;
  }

  function applyRoleVisibility() {
    document.querySelectorAll("[data-roles]").forEach(function (el) {
      var roles = (el.getAttribute("data-roles") || "").split(/\s+/);
      el.hidden = roles.indexOf(me.role) < 0;
    });
  }

  function showView(v) {
    currentView = v;
    document.querySelectorAll("#sidebar button").forEach(function (b) {
      b.classList.toggle("active", b.getAttribute("data-view") === v);
    });
    document.querySelectorAll("main .view").forEach(function (sec) {
      sec.hidden = sec.id !== "view-" + v;
    });
    if (v === "home") renderMe();
    if (v === "doctors") loadDoctors();
    if (v === "patients") loadPatients();
    if (v === "appointments") {
      loadDoctorSelect();
      loadAppointments();
      setupAppointmentForm();
    }
    if (v === "records") setupRecordsForm();
    if (v === "invoices") {
      loadInvoices();
    }
  }

  function buildNav() {
    var def = [
      { id: "home", label: "Home" },
      { id: "doctors", label: "Doctors", need: "admin" },
      { id: "patients", label: "Patients", need: "staff_pd" },
      { id: "appointments", label: "Appointments", need: "all" },
      { id: "records", label: "Records", need: "dr_ad" },
      { id: "invoices", label: "Invoices", need: "inv" },
    ];
    var sb = document.getElementById("sidebar");
    def.forEach(function (item) {
      var ok = true;
      if (item.need === "admin") ok = me.role === "admin";
      else if (item.need === "staff_pd")
        ok = /^(admin|receptionist|doctor)$/.test(me.role);
      else if (item.need === "dr_ad") ok = /^(admin|doctor)$/.test(me.role);
      else if (item.need === "inv")
        ok = /^(admin|receptionist|patient)$/.test(me.role);
      if (!ok) return;
      var b = document.createElement("button");
      b.type = "button";
      b.textContent = item.label;
      b.setAttribute("data-view", item.id);
      b.addEventListener("click", function () {
        showView(item.id);
      });
      sb.appendChild(b);
    });
  }

  function renderMe() {
    var box = document.getElementById("me-box");
    if (!me) return;
    box.innerHTML =
      "<p><strong>Email</strong> " +
      esc(me.email) +
      "</p>" +
      "<p><strong>Role</strong> " +
      esc(me.role) +
      "</p>" +
      "<p><strong>User id</strong> " +
      me.id +
      (me.patient_id != null ? " · <strong>Patient id</strong> " + me.patient_id : "") +
      (me.doctor_id != null ? " · <strong>Doctor id</strong> " + me.doctor_id : "") +
      "</p>";
  }

  async function loadDoctors() {
    var t = document.getElementById("table-doctors");
    try {
      var data = await api("/doctors?limit=200");
      var rows = (data.items || []).map(function (d) {
        return (
          "<tr><td>" +
          d.id +
          "</td><td>" +
          esc(d.full_name) +
          "</td><td>" +
          esc(d.email) +
          "</td><td>" +
          esc(d.specialization) +
          "</td><td>" +
          esc(d.department) +
          "</td></tr>"
        );
      });
      t.innerHTML =
        '<table class="data-table"><thead><tr><th>Id</th><th>Name</th><th>Email</th><th>Spec</th><th>Dept</th></tr></thead><tbody>' +
        (rows.length
          ? rows.join("")
          : '<tr><td class="empty" colspan="5">No doctors</td></tr>') +
        "</tbody></table>";
    } catch (e) {
      t.innerHTML = "<p class=\"hint\">" + esc((e.data && e.data.detail) || e) + "</p>";
    }
  }

  async function loadPatients() {
    var t = document.getElementById("table-patients");
    try {
      var data = await api("/patients?limit=200");
      var rows = (data.items || []).map(function (p) {
        return (
          "<tr><td>" +
          p.id +
          "</td><td>" +
          esc(p.full_name) +
          "</td><td>" +
          esc(p.email) +
          "</td><td>" +
          esc(p.phone) +
          "</td></tr>"
        );
      });
      t.innerHTML =
        '<table class="data-table"><thead><tr><th>Id</th><th>Name</th><th>Email</th><th>Phone</th></tr></thead><tbody>' +
        (rows.length
          ? rows.join("")
          : '<tr><td class="empty" colspan="4">No patients</td></tr>') +
        "</tbody></table>";
    } catch (e) {
      t.innerHTML = "<p class=\"hint\">" + esc((e.data && e.data.detail) || e) + "</p>";
    }
  }

  async function loadDoctorSelect() {
    var sel = document.getElementById("sel-doctor");
    if (!sel) return;
    sel.innerHTML = "";
    try {
      var data = await api("/doctors?limit=500");
      (data.items || []).forEach(function (d) {
        var o = document.createElement("option");
        o.value = d.id;
        o.textContent = d.id + " — " + d.full_name;
        sel.appendChild(o);
      });
    } catch (e) {
      toast(String((e.data && e.data.detail) || e), true);
    }
  }

  function setupAppointmentForm() {
    var wrap = document.getElementById("appt-patient-wrap");
    var inp = document.getElementById("in-patient-id");
    if (me.role === "patient") {
      if (me.patient_id == null) {
        inp.value = "";
        inp.placeholder = "No patient profile";
        inp.required = true;
        toast("Your account has no patient profile — use staff or register as patient.", true);
      } else {
        inp.value = me.patient_id;
        inp.readOnly = true;
        inp.required = true;
      }
    } else {
      inp.readOnly = false;
      inp.required = true;
    }
  }

  async function loadAppointments() {
    var t = document.getElementById("table-appointments");
    try {
      var data = await api("/appointments?limit=200");
      var rows = (data.items || []).map(function (a) {
        return (
          "<tr><td>" +
          a.id +
          "</td><td>" +
          a.patient_id +
          "</td><td>" +
          a.doctor_id +
          "</td><td>" +
          esc(a.scheduled_at) +
          "</td><td>" +
          esc(a.status) +
          "</td><td>" +
          esc(a.reason) +
          "</td></tr>"
        );
      });
      t.innerHTML =
        '<table class="data-table"><thead><tr><th>Id</th><th>Pat</th><th>Doc</th><th>When</th><th>Status</th><th>Reason</th></tr></thead><tbody>' +
        (rows.length
          ? rows.join("")
          : '<tr><td class="empty" colspan="6">No appointments</td></tr>') +
        "</tbody></table>";
    } catch (e) {
      t.innerHTML = "<p class=\"hint\">" + esc((e.data && e.data.detail) || e) + "</p>";
    }
  }

  function setupRecordsForm() {
    var did = document.getElementById("rec-did");
    if (me.role === "doctor" && me.doctor_id != null) {
      did.value = me.doctor_id;
      did.readOnly = true;
    } else {
      did.readOnly = false;
    }
    var h = document.getElementById("record-filter-hint");
    if (h) {
      h.textContent =
        me.role === "admin"
          ? "List: leave filter empty and click Load to fetch recent records (all patients), or enter a patient id."
          : "Doctors: enter a patient id and click Load to list that patient’s records.";
    }
  }

  async function loadRecordTable(patientId) {
    var t = document.getElementById("table-records");
    var path = "/medical-records?limit=100";
    if (me.role === "doctor") {
      if (!patientId) {
        t.innerHTML = "<p class=\"empty\">Enter a patient id above, then Load.</p>";
        return;
      }
      path += "&patient_id=" + encodeURIComponent(patientId);
    } else if (me.role === "admin") {
      if (patientId) path += "&patient_id=" + encodeURIComponent(patientId);
    } else {
      t.innerHTML = "<p class=\"empty\">Not available</p>";
      return;
    }
    try {
      var data = await api(path);
      var rows = (data.items || []).map(function (r) {
        return (
          "<tr><td>" +
          r.id +
          "</td><td>" +
          r.patient_id +
          "</td><td>" +
          r.doctor_id +
          "</td><td>" +
          esc(r.diagnosis) +
          "</td><td>" +
          esc(r.recorded_at) +
          "</td></tr>"
        );
      });
      t.innerHTML =
        '<table class="data-table"><thead><tr><th>Id</th><th>Pat</th><th>Doc</th><th>Diagnosis</th><th>Recorded</th></tr></thead><tbody>' +
        (rows.length
          ? rows.join("")
          : '<tr><td class="empty" colspan="5">No records</td></tr>') +
        "</tbody></table>";
    } catch (e) {
      t.innerHTML = "<p class=\"hint\">" + esc((e.data && e.data.detail) || e) + "</p>";
    }
  }

  async function loadInvoices() {
    var t = document.getElementById("table-invoices");
    try {
      var data = await api("/invoices?limit=200");
      var rows = (data.items || []).map(function (inv) {
        var st = inv.status;
        return (
          "<tr data-id=\"" +
          inv.id +
          "\"><td>" +
          inv.id +
          "</td><td>" +
          inv.patient_id +
          "</td><td>" +
          (inv.amount_total != null ? inv.amount_total : "") +
          "</td><td>" +
          esc(st) +
          "</td><td class=\"act\">" +
          (/^(admin|receptionist)$/.test(me.role) && st === "pending"
            ? "<button type=\"button\" class=\"mark-paid small\">Mark paid</button>"
            : "") +
          "</td></tr>"
        );
      });
      t.innerHTML =
        '<table class="data-table" id="tbl-inv"><thead><tr><th>Id</th><th>Patient</th><th>Total</th><th>Status</th><th></th></tr></thead><tbody>' +
        (rows.length
          ? rows.join("")
          : '<tr><td class="empty" colspan="5">No invoices</td></tr>') +
        "</tbody></table>";
      t.querySelectorAll(".mark-paid").forEach(function (btn) {
        btn.addEventListener("click", function () {
          var tr = btn.closest("tr");
          var id = tr && tr.getAttribute("data-id");
          if (id) markInvoicePaid(id);
        });
      });
    } catch (e) {
      t.innerHTML = "<p class=\"hint\">" + esc((e.data && e.data.detail) || e) + "</p>";
    }
  }

  async function markInvoicePaid(id) {
    try {
      await api("/invoices/" + id + "/status", {
        method: "PATCH",
        body: JSON.stringify({ status: "paid" }),
      });
      toast("Invoice " + id + " marked paid");
      loadInvoices();
    } catch (e) {
      toast(String((e.data && e.data.detail) || e), true);
    }
  }

  function wireForms() {
    document.getElementById("btn-logout").addEventListener("click", function () {
      HmsApi.clearToken();
      location.href = "/";
    });

    var fr = document.getElementById("form-reception");
    if (fr) {
      fr.addEventListener("submit", async function (e) {
        e.preventDefault();
        var fd = new FormData(fr);
        try {
          await api("/auth/register/receptionist", {
            method: "POST",
            body: JSON.stringify({
              email: fd.get("email").trim(),
              password: fd.get("password"),
              full_name: fd.get("full_name").trim(),
            }),
          });
          fr.reset();
          toast("Receptionist created");
        } catch (err) {
          toast(String((err.data && err.data.detail) || err), true);
        }
      });
    }

    var fd = document.getElementById("form-doctor");
    if (fd) {
      fd.addEventListener("submit", async function (e) {
        e.preventDefault();
        var f = new FormData(fd);
        try {
          await api("/doctors", {
            method: "POST",
            body: JSON.stringify({
              email: f.get("email").trim(),
              password: f.get("password"),
              full_name: f.get("full_name").trim(),
              specialization: (f.get("specialization") || "").trim() || null,
              license_number: (f.get("license_number") || "").trim() || null,
              department: (f.get("department") || "").trim() || null,
            }),
          });
          fd.reset();
          toast("Doctor added");
          loadDoctors();
        } catch (err) {
          toast(String((err.data && err.data.detail) || err), true);
        }
      });
    }

    var fp = document.getElementById("form-patient");
    if (fp) {
      fp.addEventListener("submit", async function (e) {
        e.preventDefault();
        var f = new FormData(fp);
        var dob = f.get("date_of_birth");
        try {
          await api("/patients", {
            method: "POST",
            body: JSON.stringify({
              email: f.get("email").trim(),
              password: f.get("password"),
              full_name: f.get("full_name").trim(),
              date_of_birth: dob || null,
              phone: (f.get("phone") || "").trim() || null,
              address: (f.get("address") || "").trim() || null,
              emergency_contact: (f.get("emergency_contact") || "").trim() || null,
            }),
          });
          fp.reset();
          toast("Patient added");
          loadPatients();
        } catch (err) {
          toast(String((err.data && err.data.detail) || err), true);
        }
      });
    }

    var fa = document.getElementById("form-appointment");
    if (fa) {
      fa.addEventListener("submit", async function (e) {
        e.preventDefault();
        var f = new FormData(fa);
        var pid = f.get("patient_id");
        if (me.role === "patient") {
          if (me.patient_id == null) {
            toast("This account has no patient id — cannot book.", true);
            return;
          }
          pid = me.patient_id;
        }
        var dt = document.getElementById("in-appt-time").value;
        if (!dt) {
          toast("Pick a date and time", true);
          return;
        }
        var iso = new Date(dt).toISOString();
        try {
          await api("/appointments", {
            method: "POST",
            body: JSON.stringify({
              patient_id: parseInt(String(pid), 10),
              doctor_id: parseInt(String(f.get("doctor_id")), 10),
              scheduled_at: iso,
              reason: (f.get("reason") || "").trim() || null,
            }),
          });
          fa.querySelector("#in-appt-time").value = "";
          fa.querySelector("[name=reason]").value = "";
          toast("Appointment created");
          loadAppointments();
        } catch (err) {
          toast(String((err.data && err.data.detail) || err), true);
        }
      });
    }

    var fr2 = document.getElementById("form-record");
    if (fr2) {
      fr2.addEventListener("submit", async function (e) {
        e.preventDefault();
        var f = new FormData(fr2);
        var aid = f.get("appointment_id");
        try {
          await api("/medical-records", {
            method: "POST",
            body: JSON.stringify({
              patient_id: parseInt(String(f.get("patient_id")), 10),
              doctor_id: parseInt(String(f.get("doctor_id")), 10),
              appointment_id: aid ? parseInt(String(aid), 10) : null,
              diagnosis: (f.get("diagnosis") || "").trim() || null,
              notes: (f.get("notes") || "").trim() || null,
              prescription: (f.get("prescription") || "").trim() || null,
            }),
          });
          ["diagnosis", "notes", "prescription"].forEach(function (n) {
            var el = fr2.querySelector("[name=\"" + n + "\"]");
            if (el) el.value = "";
          });
          var ra = fr2.querySelector("#rec-aid");
          if (ra) ra.value = "";
          if (me.role !== "doctor") {
            var rp = fr2.querySelector("#rec-pid");
            if (rp) rp.value = "";
          }
          toast("Record saved");
          var lid = document.getElementById("list-rec-pid");
          if (lid && lid.value) loadRecordTable(lid.value);
        } catch (err) {
          toast(String((err.data && err.data.detail) || err), true);
        }
      });
    }

    var btnLr = document.getElementById("btn-load-records");
    if (btnLr) {
      btnLr.addEventListener("click", function () {
        var pid = document.getElementById("list-rec-pid").value;
        if (me.role === "doctor" && !pid) {
          toast("Enter patient id for doctors", true);
          return;
        }
        loadRecordTable(pid || null);
      });
    }

    var fi = document.getElementById("form-invoice");
    if (fi) {
      fi.addEventListener("submit", async function (e) {
        e.preventDefault();
        var lines = [];
        document.querySelectorAll("#inv-lines .inv-line").forEach(function (row) {
          var d = row.querySelector(".d").value.trim();
          var q = parseFloat(row.querySelector(".q").value) || 1;
          var u = parseFloat(row.querySelector(".u").value) || 0;
          if (d) lines.push({ description: d, quantity: q, unit_price: u });
        });
        if (!lines.length) {
          toast("Add at least one line item with description and price", true);
          return;
        }
        var f = new FormData(fi);
        var ap = f.get("appointment_id");
        try {
          await api("/invoices", {
            method: "POST",
            body: JSON.stringify({
              patient_id: parseInt(String(f.get("patient_id")), 10),
              appointment_id: ap ? parseInt(String(ap), 10) : null,
              due_date: f.get("due_date") || null,
              description: (f.get("description") || "").trim() || null,
              lines: lines,
            }),
          });
          fi.reset();
          document.querySelector("#inv-lines").innerHTML =
            '<div class="grid-2 inv-line">' +
            '<div><label>Description</label><input class="d" placeholder="e.g. Consultation" /></div>' +
            '<div><label>Qty</label><input class="q" type="number" value="1" min="0" step="0.01" /></div>' +
            '<div><label>Unit price</label><input class="u" type="number" value="0" min="0" step="0.01" /></div></div>';
          toast("Invoice created");
          loadInvoices();
        } catch (err) {
          toast(String((err.data && err.data.detail) || err), true);
        }
      });
    }

    var addLine = document.getElementById("btn-add-line");
    if (addLine) {
      addLine.addEventListener("click", function () {
        var box = document.getElementById("inv-lines");
        var d = document.createElement("div");
        d.className = "grid-2 inv-line";
        d.innerHTML =
          '<div><label>Description</label><input class="d" /></div>' +
          '<div><label>Qty</label><input class="q" type="number" value="1" min="0" step="0.01" /></div>' +
          '<div><label>Unit price</label><input class="u" type="number" value="0" min="0" step="0.01" /></div>';
        box.appendChild(d);
      });
    }
  }

  async function init() {
    try {
      me = await api("/auth/me");
    } catch (e) {
      HmsApi.clearToken();
      location.href = "/";
      return;
    }
    document.getElementById("header-user").textContent = me.full_name + " · " + me.role;
    buildNav();
    applyRoleVisibility();
    wireForms();
    showView("home");
  }

  init();
})();
