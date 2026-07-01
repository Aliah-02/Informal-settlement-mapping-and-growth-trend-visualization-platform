/**
 * Environment configuration for local dev and production (Vercel + Render).
 */
(function () {
  if (typeof window.DARINFORMAL_API_URL === 'undefined' || !window.DARINFORMAL_API_URL) {
    const isLocalDev =
      window.location.port === '5500' ||
      window.location.port === '3000' ||
      window.location.hostname === '127.0.0.1' ||
      window.location.hostname === 'localhost';

    if (isLocalDev) {
      window.DARINFORMAL_API_URL = 'http://localhost:8000/api';
    }
  }
})();
