/**
 * DarInformal API client module.
 * Handles all backend communication with error handling and loading states.
 */

const API = (() => {
  const BASE_URL = window.DARINFORMAL_API_URL || '/api';

  async function request(endpoint, options = {}) {
    const url = `${BASE_URL}${endpoint}`;
    const response = await fetch(url, {
      headers: { 'Accept': 'application/json', ...options.headers },
      ...options,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail || `API error: ${response.status}`);
    }
    return response.json();
  }

  return {
    async getHealth() {
      return request('/health');
    },

    async getRiskLayer(year) {
      return request(`/risk/${year}`);
    },

    async getMetricsTrend() {
      return request('/metrics/trend');
    },

    async getChangeDetection(fromYear, toYear) {
      return request(`/change/${fromYear}/${toYear}`);
    },

    async getSettlements(params = {}) {
      const query = new URLSearchParams();
      Object.entries(params).forEach(([key, val]) => {
        if (val !== null && val !== undefined) query.set(key, val);
      });
      const qs = query.toString();
      return request(`/settlements${qs ? '?' + qs : ''}`);
    },

    async getAOI() {
      return request('/aoi');
    },

    getGrowthTrendCsvUrl() {
      return `${BASE_URL}/metrics/trend/csv`;
    },

    getChangeDetectionCsvUrl(fromYear, toYear) {
      return `${BASE_URL}/change/${fromYear}/${toYear}/csv`;
    },

    async downloadFile(url, filename) {
      try {
        const response = await fetch(url);
        if (!response.ok) {
          throw new Error(`Download failed: ${response.status}`);
        }
        const blob = await response.blob();
        const blobUrl = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = blobUrl;
        a.download = filename || 'report.csv';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(blobUrl);
      } catch (err) {
        console.warn('Blob download failed, opening URL:', err);
        window.open(url, '_blank', 'noopener');
      }
    },
  };
})();

window.API = API;
