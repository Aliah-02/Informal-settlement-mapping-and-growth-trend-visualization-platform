/**
 * Analytics Dashboard Module
 * Chart.js visualizations and KPI cards for settlement metrics.
 */

const Dashboard = (() => {
  let areaChart = null;
  let isiChart = null;
  let riskChart = null;
  let trendData = null;

  const CHART_DEFAULTS = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { labels: { color: '#94a3b8', font: { size: 11 } } },
    },
    scales: {
      x: { ticks: { color: '#64748b' }, grid: { color: 'rgba(100,116,139,0.15)' } },
      y: { ticks: { color: '#64748b' }, grid: { color: 'rgba(100,116,139,0.15)' } },
    },
  };

  async function init() {
    try {
      trendData = await API.getMetricsTrend();
      updateKPIs(trendData);
      renderCharts(trendData);
      renderRiskBreakdown(trendData);
    } catch (err) {
      console.error('Dashboard init failed:', err);
      showError('Failed to load analytics data');
    }
  }

  function updateKPIs(data) {
    if (!data.metrics || data.metrics.length === 0) return;

    const latest = data.metrics[data.metrics.length - 1];
    const summary = data.summary || {};

    setText('kpi-settlements', latest.total_settlements.toLocaleString());
    setText('kpi-area', `${latest.total_area_ha.toLocaleString()} ha`);
    setText('kpi-isi', latest.average_isi.toFixed(3));
    setText('kpi-high-risk', `${latest.high_risk_area_ha.toLocaleString()} ha`);
    setText('kpi-population', latest.population_proxy_total.toLocaleString());
    setText('kpi-growth', summary.total_area_growth_pct != null
      ? `${summary.total_area_growth_pct > 0 ? '+' : ''}${summary.total_area_growth_pct}%`
      : '—'
    );

    const growthEl = document.getElementById('kpi-growth');
    if (growthEl && summary.total_area_growth_pct != null) {
      growthEl.classList.toggle('positive', summary.total_area_growth_pct > 0);
      growthEl.classList.toggle('negative', summary.total_area_growth_pct < 0);
    }
  }

  function renderCharts(data) {
    const years = data.years;
    const metrics = data.metrics;

    // Area growth chart
    const areaCtx = document.getElementById('area-chart');
    if (areaCtx) {
      if (areaChart) areaChart.destroy();
      areaChart = new Chart(areaCtx, {
        type: 'bar',
        data: {
          labels: years,
          datasets: [
            {
              label: 'Total Area (ha)',
              data: metrics.map((m) => m.total_area_ha),
              backgroundColor: 'rgba(59, 130, 246, 0.6)',
              borderColor: '#3b82f6',
              borderWidth: 1,
            },
            {
              label: 'High Risk Area (ha)',
              data: metrics.map((m) => m.high_risk_area_ha),
              backgroundColor: 'rgba(239, 68, 68, 0.6)',
              borderColor: '#ef4444',
              borderWidth: 1,
            },
          ],
        },
        options: { ...CHART_DEFAULTS, plugins: { ...CHART_DEFAULTS.plugins, title: { display: false } } },
      });
    }

    // ISI trend line chart
    const isiCtx = document.getElementById('isi-chart');
    if (isiCtx) {
      if (isiChart) isiChart.destroy();
      isiChart = new Chart(isiCtx, {
        type: 'line',
        data: {
          labels: years,
          datasets: [{
            label: 'Average ISI',
            data: metrics.map((m) => m.average_isi),
            borderColor: '#f59e0b',
            backgroundColor: 'rgba(245, 158, 11, 0.1)',
            fill: true,
            tension: 0.3,
            pointRadius: 5,
            pointBackgroundColor: '#f59e0b',
          }],
        },
        options: {
          ...CHART_DEFAULTS,
          scales: {
            ...CHART_DEFAULTS.scales,
            y: { ...CHART_DEFAULTS.scales.y, min: 0, max: 1 },
          },
        },
      });
    }

    // Risk distribution doughnut for latest year
    const riskCtx = document.getElementById('risk-chart');
    if (riskCtx && metrics.length > 0) {
      const latest = metrics[metrics.length - 1];
      if (riskChart) riskChart.destroy();
      riskChart = new Chart(riskCtx, {
        type: 'doughnut',
        data: {
          labels: ['Low Risk', 'Medium Risk', 'High Risk'],
          datasets: [{
            data: [latest.low_risk_area_ha, latest.medium_risk_area_ha, latest.high_risk_area_ha],
            backgroundColor: ['#22c55e', '#f59e0b', '#ef4444'],
            borderWidth: 0,
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'bottom', labels: { color: '#94a3b8', font: { size: 10 }, padding: 8 } },
          },
        },
      });
    }
  }

  function renderRiskBreakdown(data) {
    const container = document.getElementById('risk-breakdown');
    if (!container || !data.metrics || data.metrics.length === 0) return;

    const latest = data.metrics[data.metrics.length - 1];
    const total = latest.total_area_ha || 1;

    container.innerHTML = [
      { level: 'high', label: 'High Risk', area: latest.high_risk_area_ha, count: latest.high_risk_count, color: '#ef4444' },
      { level: 'medium', label: 'Medium Risk', area: latest.medium_risk_area_ha, count: latest.medium_risk_count, color: '#f59e0b' },
      { level: 'low', label: 'Low Risk', area: latest.low_risk_area_ha, count: latest.low_risk_count, color: '#22c55e' },
    ].map((r) => `
      <div class="risk-bar-item">
        <div class="risk-bar-header">
          <span class="risk-dot" style="background:${r.color}"></span>
          <span>${r.label}</span>
          <span class="risk-bar-count">${r.count} settlements</span>
        </div>
        <div class="risk-bar-track">
          <div class="risk-bar-fill" style="width:${(r.area / total * 100).toFixed(1)}%;background:${r.color}"></div>
        </div>
        <div class="risk-bar-value">${r.area.toFixed(1)} ha (${(r.area / total * 100).toFixed(1)}%)</div>
      </div>
    `).join('');
  }

  function updateForYear(year) {
    if (!trendData) return;
    const m = trendData.metrics.find((x) => x.year === year);
    if (!m) return;

    setText('kpi-settlements', m.total_settlements.toLocaleString());
    setText('kpi-area', `${m.total_area_ha.toLocaleString()} ha`);
    setText('kpi-isi', m.average_isi.toFixed(3));
    setText('kpi-high-risk', `${m.high_risk_area_ha.toLocaleString()} ha`);
    setText('kpi-population', m.population_proxy_total.toLocaleString());

    const growthEl = document.getElementById('kpi-growth');
    if (growthEl) {
      if (m.growth_rate_pct != null) {
        setText('kpi-growth', `${m.growth_rate_pct > 0 ? '+' : ''}${m.growth_rate_pct}%`);
        growthEl.classList.toggle('positive', m.growth_rate_pct > 0);
        growthEl.classList.toggle('negative', m.growth_rate_pct < 0);
      } else {
        setText('kpi-growth', '—');
      }
    }
  }

  function showChangeSummary(changeData) {
    const panel = document.getElementById('change-summary');
    if (!panel || !changeData) return;

    const s = changeData.summary;
    panel.classList.add('visible');
    panel.innerHTML = `
      <h4>Change: ${changeData.from_year} → ${changeData.to_year}</h4>
      <div class="change-stats">
        <div class="change-stat new"><span class="num">${s.new_count}</span><span class="lbl">New</span></div>
        <div class="change-stat expanded"><span class="num">${s.expanded_count}</span><span class="lbl">Expanded</span></div>
        <div class="change-stat contracted"><span class="num">${s.contracted_count}</span><span class="lbl">Contracted</span></div>
        <div class="change-stat stable"><span class="num">${s.stable_count}</span><span class="lbl">Stable</span></div>
      </div>
      <div class="change-detail">
        Area change: <strong>${s.area_change_pct > 0 ? '+' : ''}${s.area_change_pct}%</strong>
        (${changeData.area_change_ha > 0 ? '+' : ''}${changeData.area_change_ha} ha)
      </div>
    `;
  }

  function hideChangeSummary() {
    const panel = document.getElementById('change-summary');
    if (panel) panel.classList.remove('visible');
  }

  function setText(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
  }

  function showError(msg) {
    const el = document.getElementById('dashboard-error');
    if (el) { el.textContent = msg; el.style.display = 'block'; }
  }

  return { init, updateForYear, showChangeSummary, hideChangeSummary };
})();

window.Dashboard = Dashboard;
