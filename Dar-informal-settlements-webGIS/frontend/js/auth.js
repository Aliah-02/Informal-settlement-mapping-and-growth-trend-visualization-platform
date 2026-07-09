/**
 * Authentication — signup, login, session token, role-based redirect.
 */
const Auth = (() => {
  const TOKEN_KEY = 'darinformal-token';
  const USER_KEY = 'darinformal-user';
  const SESSION_KEY = 'darinformal-session';

  function getSessionToken() {
    let token = localStorage.getItem(SESSION_KEY);
    if (!token) {
      token = crypto.randomUUID().replace(/-/g, '');
      localStorage.setItem(SESSION_KEY, token);
    }
    return token;
  }

  function getToken() {
    return localStorage.getItem(TOKEN_KEY);
  }

  function getUser() {
    try {
      const raw = localStorage.getItem(USER_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  }

  function isAdmin() {
    return getUser()?.role === 'admin';
  }

  function isLoggedIn() {
    return Boolean(getToken() && getUser());
  }

  function setSession(auth) {
    localStorage.setItem(TOKEN_KEY, auth.access_token);
    localStorage.setItem(USER_KEY, JSON.stringify(auth.user));
  }

  function logout() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    window.location.href = 'auth.html';
  }

  function authHeaders(extra = {}) {
    const headers = {
      'X-Session-Token': getSessionToken(),
      ...extra,
    };
    const token = getToken();
    if (token) headers.Authorization = `Bearer ${token}`;
    return headers;
  }

  async function signup(form) {
    const body = {
      first_name: form.first_name.value.trim(),
      last_name: form.last_name.value.trim(),
      email: form.email.value.trim(),
      mobile: form.mobile.value.trim() || null,
      password: form.password.value,
      confirm_password: form.confirm_password.value,
      company_name: form.company_name?.value?.trim() || null,
    };
    let res;
    try {
      res = await fetch(`${API.BASE}/auth/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authHeaders() },
        body: JSON.stringify(body),
      });
    } catch {
      throw new Error(
        'Cannot reach API server. Wait for Render cold start (~60s) or check DARINFORMAL_API_URL on Vercel.'
      );
    }
    const data = await res.json().catch(() => ({}));
    const detail = Array.isArray(data.detail)
      ? data.detail[0]?.msg
      : data.detail;
    if (!res.ok) throw new Error(detail || `Signup failed (${res.status})`);
    setSession(data);
    return data;
  }

  async function login(form) {
    const body = {
      email: form.email.value.trim(),
      password: form.password.value,
    };
    let res;
    try {
      res = await fetch(`${API.BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authHeaders() },
        body: JSON.stringify(body),
      });
    } catch {
      throw new Error(
        'Cannot reach API server. Wait for Render cold start (~60s) or check DARINFORMAL_API_URL on Vercel.'
      );
    }
    const data = await res.json().catch(() => ({}));
    const detail = Array.isArray(data.detail)
      ? data.detail[0]?.msg
      : data.detail;
    if (!res.ok) throw new Error(detail || `Login failed (${res.status})`);
    setSession(data);
    return data;
  }

  function redirectAfterLogin(user) {
    if (user.role === 'admin') {
      window.location.href = 'admin.html';
    } else {
      window.location.href = 'index.html';
    }
  }

  function guardAdminPage() {
    if (!isLoggedIn() || !isAdmin()) {
      window.location.href = 'auth.html';
    }
  }

  function updateNavAuthLink() {
    const link = document.getElementById('nav-auth-link');
    if (!link) return;
    const user = getUser();
    if (user) {
      link.textContent = user.role === 'admin' ? 'ADMIN' : 'LOGOUT';
      link.href = user.role === 'admin' ? 'admin.html' : '#';
      if (user.role !== 'admin') {
        link.addEventListener('click', (e) => {
          e.preventDefault();
          logout();
        });
      }
    }
  }

  return {
    getSessionToken,
    getToken,
    getUser,
    isAdmin,
    isLoggedIn,
    setSession,
    logout,
    authHeaders,
    signup,
    login,
    redirectAfterLogin,
    guardAdminPage,
    updateNavAuthLink,
  };
})();

window.Auth = Auth;
