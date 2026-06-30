/**
 * Time Slider Module
 * Controls year selection (2005–2026) and change detection mode.
 */

const TimeSlider = (() => {
  const YEARS = [2005, 2010, 2015, 2020, 2026];
  let currentYear = 2020;
  let changeMode = false;
  let fromYear = 2015;
  let onYearChange = null;
  let onChangeDetection = null;

  function init(options = {}) {
    currentYear = options.defaultYear || 2020;
    onYearChange = options.onYearChange || null;
    onChangeDetection = options.onChangeDetection || null;

    const slider = document.getElementById('year-slider');
    const yearLabel = document.getElementById('year-label');
    const yearTicks = document.getElementById('year-ticks');
    const changeToggle = document.getElementById('change-mode-toggle');
    const fromSelect = document.getElementById('from-year-select');
    const toSelect = document.getElementById('to-year-select');
    const applyChangeBtn = document.getElementById('apply-change-btn');

    if (!slider) return;

    slider.min = 0;
    slider.max = YEARS.length - 1;
    slider.step = 1;
    slider.value = YEARS.indexOf(currentYear);

    // Build year tick marks
    if (yearTicks) {
      yearTicks.innerHTML = YEARS.map((y) =>
        `<span class="tick" data-year="${y}">${y}</span>`
      ).join('');
    }

    // Populate change detection selects
    [fromSelect, toSelect].forEach((sel) => {
      if (!sel) return;
      sel.innerHTML = YEARS.map((y) => `<option value="${y}">${y}</option>`).join('');
    });
    if (fromSelect) fromSelect.value = fromYear;
    if (toSelect) toSelect.value = currentYear;

    updateLabel(yearLabel);

    slider.addEventListener('input', () => {
      const idx = parseInt(slider.value, 10);
      currentYear = YEARS[idx];
      updateLabel(yearLabel);
      updateActiveTick();
      if (onYearChange && !changeMode) onYearChange(currentYear);
    });

    // Click on tick labels
    if (yearTicks) {
      yearTicks.addEventListener('click', (e) => {
        const tick = e.target.closest('.tick');
        if (!tick) return;
        const year = parseInt(tick.dataset.year, 10);
        const idx = YEARS.indexOf(year);
        if (idx >= 0) {
          slider.value = idx;
          currentYear = year;
          updateLabel(yearLabel);
          updateActiveTick();
          if (onYearChange && !changeMode) onYearChange(currentYear);
        }
      });
    }

    if (changeToggle) {
      changeToggle.addEventListener('change', () => {
        changeMode = changeToggle.checked;
        document.getElementById('slider-panel').classList.toggle('change-mode', changeMode);
        document.getElementById('change-panel').classList.toggle('visible', changeMode);
        if (!changeMode && onYearChange) onYearChange(currentYear);
      });
    }

    if (applyChangeBtn) {
      applyChangeBtn.addEventListener('click', () => {
        fromYear = parseInt(fromSelect?.value || 2015, 10);
        const toYear = parseInt(toSelect?.value || 2020, 10);
        if (fromYear >= toYear) {
          alert('From year must be earlier than To year.');
          return;
        }
        if (onChangeDetection) onChangeDetection(fromYear, toYear);
      });
    }

    updateActiveTick();
  }

  function updateLabel(el) {
    if (el) el.textContent = currentYear;
  }

  function updateActiveTick() {
    document.querySelectorAll('.tick').forEach((t) => {
      t.classList.toggle('active', parseInt(t.dataset.year, 10) === currentYear);
    });
  }

  function setYear(year) {
    const idx = YEARS.indexOf(year);
    if (idx < 0) return;
    currentYear = year;
    const slider = document.getElementById('year-slider');
    if (slider) slider.value = idx;
    updateLabel(document.getElementById('year-label'));
    updateActiveTick();
  }

  function getYear() {
    return currentYear;
  }

  function getYears() {
    return YEARS;
  }

  return { init, setYear, getYear, getYears };
})();

window.TimeSlider = TimeSlider;
