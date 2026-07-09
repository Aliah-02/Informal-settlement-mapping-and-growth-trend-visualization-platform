/**
 * Admin dashboard data loader.
 */
const AdminDashboard = (() => {
  function setText(id, val) {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
  }

  async function load() {
    try {
      const dash = await API.request('/admin/dashboard');
      setText('adm-users', dash.total_users_joined?.toLocaleString() ?? '0');
      setText('adm-live', dash.live_users?.toLocaleString() ?? '0');
      setText('adm-downloads', dash.total_downloads?.toLocaleString() ?? '0');
      setText('adm-daily', dash.daily_visitors?.toLocaleString() ?? '0');
      setText('adm-monthly', dash.monthly_visitors?.toLocaleString() ?? '0');
      setText('adm-yearly', dash.yearly_visitors?.toLocaleString() ?? '0');
      setText('adm-rate', `${dash.download_rate_pct ?? 0}%`);

      const usersBody = document.getElementById('users-tbody');
      if (usersBody) {
        usersBody.innerHTML = (dash.recent_users || []).map((u) => `
          <tr>
            <td>${u.first_name} ${u.last_name}</td>
            <td>${u.email}</td>
            <td>${u.role}</td>
            <td>${u.created_at ? new Date(u.created_at).toLocaleString() : '—'}</td>
          </tr>
        `).join('') || '<tr><td colspan="4">No users yet</td></tr>';
      }

      const dl = await API.request('/admin/downloads');
      const dlBody = document.getElementById('downloads-tbody');
      if (dlBody) {
        dlBody.innerHTML = (dl.downloads || []).map((d) => `
          <tr>
            <td>${d.user_email || 'Guest'}</td>
            <td>${d.report_label}</td>
            <td>${d.report_type}</td>
            <td>${d.ip_address || '—'}</td>
            <td>${d.downloaded_at ? new Date(d.downloaded_at).toLocaleString() : '—'}</td>
          </tr>
        `).join('') || '<tr><td colspan="5">No downloads yet</td></tr>';
      }
    } catch (err) {
      console.error('Admin load failed', err);
    }
  }

  function init() {
    load();
    setInterval(load, 30000);
  }

  return { init, load };
})();

window.AdminDashboard = AdminDashboard;
