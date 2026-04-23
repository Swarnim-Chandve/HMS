/* HMS — API client (global: HmsApi) */
(function (global) {
  const API = "/api/v1";
  const TOKEN_KEY = "hms_token";

  function getToken() {
    return localStorage.getItem(TOKEN_KEY);
  }
  function setToken(t) {
    localStorage.setItem(TOKEN_KEY, t);
  }
  function clearToken() {
    localStorage.removeItem(TOKEN_KEY);
  }

  async function api(path, opts) {
    opts = opts || {};
    var headers = { "Content-Type": "application/json" };
    if (opts.headers) {
      for (var k in opts.headers) headers[k] = opts.headers[k];
    }
    var t = getToken();
    if (t) headers["Authorization"] = "Bearer " + t;
    var res = await fetch(API + path, {
      method: opts.method || "GET",
      headers: headers,
      body: opts.body != null ? opts.body : undefined,
    });
    var text = await res.text();
    var data = null;
    if (text) {
      try {
        data = JSON.parse(text);
      } catch (e) {
        data = { detail: text };
      }
    }
    if (res.status === 401) {
      clearToken();
      if (path.indexOf("/auth/login") < 0) {
        try {
          location.href = "/";
        } catch (e) {}
      }
      throw { status: res.status, data: data };
    }
    if (!res.ok) throw { status: res.status, data: data };
    return data;
  }

  global.HmsApi = { api: api, getToken: getToken, setToken: setToken, clearToken: clearToken };
})(typeof window !== "undefined" ? window : this);
