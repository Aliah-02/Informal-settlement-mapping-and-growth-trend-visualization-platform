/**
 * API URL — set by Vercel build (js/env.js) or defaults below for local dev.
 *
 * Production (Vercel):
 *   DARINFORMAL_API_URL=https://your-api.onrender.com/api
 *
 * Local (VS Code port 5500):
 *   defaults to http://localhost:8000/api
 */
(function () {
  if (window.DARINFORMAL_API_URL) return;

  const local =
    window.location.hostname === 'localhost' ||
    window.location.hostname === '127.0.0.1';

  if (local) {
    window.DARINFORMAL_API_URL = 'http://localhost:8000/api';
  }
})();
