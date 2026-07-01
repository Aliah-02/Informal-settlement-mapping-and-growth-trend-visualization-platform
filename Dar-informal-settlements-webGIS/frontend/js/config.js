/**
 * Environment configuration for local dev and production (Vercel + Render).
 */
(function () {
  // Set by build-env.mjs on Vercel (js/env.js) or manually
  if (typeof window.DARINFORMAL_API_URL === 'undefined' || !window.DARINFORMAL_API_URL) {
    const isLocalDev =
      window.location.port === '5500' ||
      window.location.port === '3000' ||
      window.location.hostname === '127.0.0.1' ||
      window.location.hostname === 'localhost';

    if (isLocalDev) {
      window.DARINFORMAL_API_URL = 'http://localhost:8000/api';
    }
    // Production: must set DARINFORMAL_API_URL in Vercel env → build generates env.js
  }

  // GeoServer not available on Render/Vercel free tier — default to API GeoJSON
  const isCloudHost =
    window.location.hostname.includes('vercel.app') ||
    window.location.hostname.includes('onrender.com');

  if (isCloudHost && !window.DARINFORMAL_FORCE_WMS) {
    window.DARINFORMAL_DEFAULT_RENDER_MODE = 'geojson';
  }
})();
