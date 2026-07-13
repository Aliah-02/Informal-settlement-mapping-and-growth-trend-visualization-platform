/**
 * Statistics page — location analytics from settlement map data.
 */
const Statistics = (() => {
  let lineChart = null;
  let analytics = null;
  let trendData = null;

  const DISTRICT_COLORS = {
    Kinondoni: '#eab308',
    Ubungo: '#8b5cf6',
    Ilala: '#22c55e',
    Temeke: '#3b82f6',
  };

  async function load(year) {
    const [loc, trend] = await Promise.all([
      API.getLocationAnalytics(year),
      API.getMetricsTrend().catch(() => ({ years: [], metrics: [] })),
    ]);
    analytics = loc;
    trendData = trend;
    renderDistrictFilter(loc);
    renderYearFilters(loc);
    renderWardTable(loc);
    renderDistrictBars(loc);
    renderLineChart(trend, loc.year);
    updateContextText(loc);
  }

  function renderDistrictFilter(loc) {
    const sel = document.getElementById('district-filter');
    if (!sel) return;
    const districts = loc.districts?.map((d) => d.district) || [];
    sel.innerHTML = districts.map((d) => `<option value="${d}">${d}</option>`).join('');
    if (districts.length) sel.value = districts[0];
  }

  function renderYearFilters(loc) {
    const years = loc.years_available || [];
    const fromSel = document.getElementById('from-year');
    const toSel = document.getElementById('to-year');
    const growthSel = document.getElementById('growth-year');
    if (fromSel && years.length) {
      fromSel.innerHTML = years.slice(0, -1).map((y) => `<option value="${y}">${y}</option>`).join('');
    }
    if (toSel && years.length) {
      toSel.innerHTML = years.slice(1).map((y) => `<option value="${y}">${y}</option>`).join('');
      toSel.value = loc.year;
    }
    if (growthSel) {
      growthSel.innerHTML = years.map((y) => `<option value="${y}">for ${y}</option>`).join('');
      growthSel.value = loc.year;
    }
  }

  function renderWardTable(loc) {
    const district = document.getElementById('district-filter')?.value;
    const tbody = document.getElementById('ward-tbody');
    if (!tbody) return;
    const wards = (loc.wards || []).filter((w) => !district || w.district === district);
    tbody.innerHTML = wards.length
      ? wards.map((w) => `
        <tr>
          <td>${w.symbol}</td>
          <td>${w.name}</td>
          <td class="cyan">${w.settlements}</td>
          <td class="cyan">${w.change_pct > 0 ? '+' : ''}${w.change_pct}%</td>
        </tr>
      `).join('')
      : '<tr><td colspan="4">No settlement data for this district</td></tr>';
  }

  function renderDistrictBars(loc) {
    const container = document.getElementById('district-bars');
    const legend = document.getElementById('district-legend');
    if (!container) return;

    const districts = loc.districts || [];
    const maxGrowth = Math.max(...districts.map((d) => Math.abs(d.growth_pct)), 1);

    container.innerHTML = districts.map((d) => {
      const color = d.color || DISTRICT_COLORS[d.district] || '#94a3b8';
      const width = Math.min(100, (Math.abs(d.growth_pct) / maxGrowth) * 100);
      return `
        <div class="district-bar-row">
          <span style="width:90px;">${d.district}</span>
          <div class="district-bar-track">
            <div class="district-bar-fill" style="width:${width}%;background:${color}"></div>
          </div>
          <span>${d.growth_pct}%</span>
          <button class="btn-download-sm" type="button" data-district="${d.district}" title="Download ${d.district} report">⬇</button>
        </div>
      `;
    }).join('');

    container.querySelectorAll('.btn-download-sm').forEach((btn) => {
      btn.addEventListener('click', () => downloadReport(btn.dataset.district));
    });

    if (legend) {
      legend.innerHTML = districts.map((d) => {
        const color = d.color || DISTRICT_COLORS[d.district];
        return `<div style="margin-bottom:0.35rem;"><span style="color:${color}">●</span> ${d.district}: ${d.growth_pct}% growth · ${d.settlements} settlements</div>`;
      }).join('');
    }
  }

  function renderLineChart(trend, year) {
    const ctx = document.getElementById('stats-line-chart');
    if (!ctx || !trend.metrics?.length) return;

    const metrics = trend.metrics;
    const labels = metrics.map((m) => String(m.year));
    const district = document.getElementById('district-filter')?.value;
    const dStats = analytics?.districts?.find((d) => d.district === district);

    if (lineChart) lineChart.destroy();
    lineChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: district ? `${district} settlements trend` : 'All settlements',
            data: metrics.map((m) => m.total_settlements),
            borderColor: '#3b82f6',
            tension: 0.3,
          },
          {
            label: 'Area (ha)',
            data: metrics.map((m) => m.total_area_ha),
            borderColor: '#94a3b8',
            tension: 0.3,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: dStats
              ? `${district}: ${dStats.settlements} settlements · ${dStats.total_area_ha} ha (${year})`
              : `Analysis year ${year}`,
            color: '#c5a059',
          },
        },
      },
    });
  }

  function updateContextText(loc) {
    const el = document.getElementById('district-context');
    if (!el) return;
    const district = document.getElementById('district-filter')?.value || 'Kinondoni';
    const d = loc.districts?.find((x) => x.district === district);
    if (!d) return;
    el.textContent = `${district} has ${d.settlements} mapped unplanned settlements covering ${d.total_area_ha} ha in ${loc.year}. Average ISI is ${d.avg_isi} with ${d.high_risk_count} high-probability clusters. Growth since the previous analysis year is ${d.growth_pct}%.`;
  }

  async function downloadReport(district) {
    const year = document.getElementById('growth-year')?.value || analytics?.year;
    const url = API.getLocationCsvUrl(year, district);
    const slug = (district || 'all').toLowerCase();
    await API.downloadFile(url, `darinformal_${slug}_${year}.csv`);
  }

  function bindEvents() {
    document.getElementById('district-filter')?.addEventListener('change', () => {
      renderWardTable(analytics);
      renderLineChart(trendData, analytics?.year);
      updateContextText(analytics);
    });

    document.getElementById('growth-year')?.addEventListener('change', async (e) => {
      await load(Number(e.target.value));
    });

    document.getElementById('download-all-btn')?.addEventListener('click', () => downloadReport(null));
  }

  async function init() {
    bindEvents();
    try {
      await load();
    } catch (err) {
      console.error('Statistics load failed', err);
      const tbody = document.getElementById('ward-tbody');
      if (tbody) tbody.innerHTML = '<tr><td colspan="4">Unable to load analytics — check API connection</td></tr>';
    }
  }

  return { init, load, downloadReport };
})();

window.Statistics = Statistics;
