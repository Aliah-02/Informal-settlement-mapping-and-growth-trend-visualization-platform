/**
 * Visitor tracking — page visits, heartbeat, public stats.
 */
const Activity = (() => {
  let heartbeatTimer = null;

  async function recordVisit(pagePath) {
    try {
      await fetch(`${API.BASE}/activity/visit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...Auth.authHeaders(),
        },
        body: JSON.stringify({ page_path: pagePath }),
      });
    } catch (e) {
      console.debug('Visit tracking skipped', e);
    }
  }

  async function heartbeat() {
    try {
      await fetch(`${API.BASE}/activity/heartbeat`, {
        method: 'POST',
        headers: Auth.authHeaders(),
      });
    } catch (e) {
      console.debug('Heartbeat skipped', e);
    }
  }

  function startHeartbeat(intervalMs = 60000) {
    heartbeat();
    if (heartbeatTimer) clearInterval(heartbeatTimer);
    heartbeatTimer = setInterval(heartbeat, intervalMs);
  }

  async function loadPublicStats() {
    try {
      return await API.request('/activity/stats');
    } catch {
      return {
        daily_visitors: 0,
        monthly_visitors: 0,
        yearly_visitors: 0,
        download_rate_pct: 0,
      };
    }
  }

  function formatCount(n) {
    if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M+`;
    return Number(n).toLocaleString();
  }

  async function renderStatsStrip() {
    const stats = await loadPublicStats();
    const map = {
      'stat-daily': stats.daily_visitors,
      'stat-monthly': stats.monthly_visitors,
      'stat-yearly': stats.yearly_visitors,
      'stat-download-rate': `${stats.download_rate_pct || 0}%`,
    };
    Object.entries(map).forEach(([id, val]) => {
      const el = document.getElementById(id);
      if (!el) return;
      el.textContent = typeof val === 'number' ? formatCount(val) : val;
    });
  }

  function init(pagePath) {
    recordVisit(pagePath || window.location.pathname);
    startHeartbeat();
    renderStatsStrip();
  }

  return { init, loadPublicStats, renderStatsStrip, formatCount };
})();

window.Activity = Activity;
