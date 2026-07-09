/**
 * Shared site navigation header.
 */
const SiteNav = (() => {
  const PAGES = [
    { href: 'index.html', label: 'HOME' },
    { href: 'maps.html', label: 'MAPS' },
    { href: 'statistics.html', label: 'STATISTICS' },
    { href: 'about.html', label: 'ABOUT US' },
    { href: 'user-guide.html', label: 'USER GUIDE' },
  ];

  function renderHeader(activePage) {
    const mount = document.getElementById('site-header');
    if (!mount) return;

    const user = typeof Auth !== 'undefined' ? Auth.getUser() : null;
    const authLabel = user
      ? (user.role === 'admin' ? 'ADMIN' : 'LOGOUT')
      : 'LOGIN / SIGN UP';
    const authHref = user
      ? (user.role === 'admin' ? 'admin.html' : '#logout')
      : 'auth.html';

    mount.innerHTML = `
      <div class="site-brand">Informal Settlement Mapping and Visualization</div>
      <nav class="site-nav" aria-label="Main">
        ${PAGES.map((p) => `
          <a href="${p.href}" class="${activePage === p.href ? 'active' : ''}">${p.label}</a>
        `).join('')}
        <a href="${authHref}" id="nav-auth-link">${authLabel}</a>
      </nav>
      <div class="site-header-actions">
        <button class="btn-search" type="button" title="Search" aria-label="Search">🔍</button>
        <button class="btn-theme" id="theme-toggle" type="button" title="Toggle light/dim theme" aria-label="Toggle theme">☀️</button>
      </div>
    `;

    if (user && user.role !== 'admin') {
      document.getElementById('nav-auth-link')?.addEventListener('click', (e) => {
        e.preventDefault();
        Auth.logout();
      });
    }
  }

  function renderFooter() {
    const mount = document.getElementById('site-footer');
    if (!mount) return;
    mount.innerHTML = `
      <div>
        <h4>CONTACT US</h4>
        <p>Info@lsm2group11.com</p>
        <p>Ardhi University, Makongo, Dar-es-salaam</p>
        <p>+255 676 767 877</p>
      </div>
      <div>
        <h4>RELATED LINKS</h4>
        <p><a href="https://ahmiea.org" target="_blank" rel="noopener">Applied Human Machine Intelligence in East Africa</a></p>
        <p><a href="https://www.nbs.go.tz" target="_blank" rel="noopener">National Statistical Offices Websites</a></p>
      </div>
      <div>
        <h4>E-feedback</h4>
        <p>Tell us what you think</p>
        <input type="email" placeholder="Your email" aria-label="Feedback email" />
        <button class="btn-gold" type="button">Submit</button>
      </div>
    `;
  }

  return { renderHeader, renderFooter };
})();

window.SiteNav = SiteNav;
