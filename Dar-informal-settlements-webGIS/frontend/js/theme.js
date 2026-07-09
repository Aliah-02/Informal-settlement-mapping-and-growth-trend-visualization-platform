/**
 * Theme toggle — light / dim (dark) modes for site pages.
 */
const Theme = (() => {
  const KEY = 'darinformal-theme';

  function apply(theme) {
    const isDark = theme !== 'light';
    document.body.classList.toggle('site-light', !isDark);
    document.body.classList.toggle('dark-mode', isDark);
    document.body.classList.toggle('light-mode', !isDark);
    const btn = document.getElementById('theme-toggle');
    if (btn) btn.textContent = isDark ? '☀️' : '🌙';
  }

  function init() {
    const saved = localStorage.getItem(KEY) || 'dark';
    apply(saved);
    document.getElementById('theme-toggle')?.addEventListener('click', () => {
      const next = document.body.classList.contains('site-light') ? 'dark' : 'light';
      localStorage.setItem(KEY, next);
      apply(next);
    });
  }

  return { init, apply };
})();

window.Theme = Theme;
