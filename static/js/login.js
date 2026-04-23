(function () {
  var api = HmsApi.api;
  var setToken = HmsApi.setToken;

  function showToast(msg, isError) {
    var el = document.getElementById("toast");
    if (!el) return;
    el.textContent = msg;
    el.className = isError ? "error show" : "ok show";
    el.style.display = "block";
    setTimeout(function () {
      el.className = "";
      el.style.display = "none";
    }, 4000);
  }

  var tabs = document.querySelectorAll(".tab");
  var panels = document.querySelectorAll(".panel");
  tabs.forEach(function (tab) {
    tab.addEventListener("click", function () {
      var id = tab.getAttribute("data-panel");
      tabs.forEach(function (t) {
        t.setAttribute("aria-selected", t === tab);
      });
      panels.forEach(function (p) {
        p.hidden = p.id !== "panel-" + id;
      });
    });
  });

  document.getElementById("form-login").addEventListener("submit", async function (e) {
    e.preventDefault();
    var fd = new FormData(e.target);
    try {
      var out = await api("/auth/login", {
        method: "POST",
        body: JSON.stringify({
          email: fd.get("email").trim(),
          password: fd.get("password"),
        }),
      });
      setToken(out.access_token);
      location.href = "/app";
    } catch (err) {
      var m =
        (err.data && (err.data.detail || err.data.message)) || err.status || "Login failed";
      if (typeof m === "object") m = JSON.stringify(m);
      showToast(String(m), true);
    }
  });

  document.getElementById("form-register").addEventListener("submit", async function (e) {
    e.preventDefault();
    var fd = new FormData(e.target);
    var dob = fd.get("date_of_birth");
    var body = {
      email: fd.get("email").trim(),
      password: fd.get("password"),
      full_name: fd.get("full_name").trim(),
      date_of_birth: dob || null,
      phone: (fd.get("phone") || "").trim() || null,
      address: (fd.get("address") || "").trim() || null,
      emergency_contact: (fd.get("emergency_contact") || "").trim() || null,
    };
    try {
      await api("/auth/register/patient", { method: "POST", body: JSON.stringify(body) });
      var loginOut = await api("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email: body.email, password: body.password }),
      });
      setToken(loginOut.access_token);
      location.href = "/app";
    } catch (err) {
      var m =
        (err.data && err.data.errors && err.data.errors[0] && err.data.errors[0].message) ||
        err.data ||
        (err.data && err.data.detail) ||
        "Register failed";
      if (m && m.detail) m = m.detail;
      if (Array.isArray(m)) m = m[0] && m[0].msg;
      if (typeof m === "object") m = m.detail || JSON.stringify(m);
      showToast(String(m), true);
    }
  });
})();
