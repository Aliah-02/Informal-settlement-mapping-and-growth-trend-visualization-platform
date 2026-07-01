/**
 * Local development configuration.
 * Adjust URLs when running outside Docker/Nginx.
 */
(function () {
  const isLocalDev =
    window.location.port === '5500' ||
    window.location.port === '3000' ||
    window.location.hostname === '127.0.0.1';

  if (isLocalDev && !window.DARINFORMAL_API_URL) {
    window.DARINFORMAL_API_URL = 'http://localhost:8000/api';
  }
})();
