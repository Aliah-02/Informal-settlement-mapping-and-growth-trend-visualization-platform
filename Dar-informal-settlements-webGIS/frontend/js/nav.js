/**
 * Shared site navigation header with user account menu.
 */
const SiteNav = (() => {
  const PAGES = [
    { href: 'index.html', label: 'HOME' },
    { href: 'maps.html', label: 'MAPS' },
    { href: 'statistics.html', label: 'STATISTICS' },
    { href: 'about.html', label: 'ABOUT US' },
    { href: 'user-guide.html', label: 'USER GUIDE' },
  ];

  function bindUserMenu() {
    const btn = document.getElementById('user-menu-btn');
    const menu = document.getElementById('user-menu-dropdown');
    if (!btn || !menu) return;

    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      menu.classList.toggle('open');
    });

    document.addEventListener('click', () => menu.classList.remove('open'));

    menu.querySelector('[data-action="logout"]')?.addEventListener('click', (e) => {
      e.preventDefault();
      if (typeof Auth !== 'undefined') Auth.logout();
    });
  }

  function renderHeader(activePage) {
    const mount = document.getElementById('site-header');
    if (!mount) return;

    const user = typeof Auth !== 'undefined' ? Auth.getUser() : null;

    let userMenuHtml;
    if (user) {
      const displayName = `${user.first_name} ${user.last_name}`.trim() || user.email;
      const roleLabel = user.role === 'admin' ? ' (Admin)' : '';
      userMenuHtml = `
        <div class="user-menu" id="user-menu">
          <button class="btn-user" id="user-menu-btn" type="button" title="Account" aria-label="Account menu">👤</button>
          <div class="user-menu-dropdown" id="user-menu-dropdown">
            <div class="user-menu-name">${displayName}${roleLabel}</div>
            <div class="user-menu-email">${user.email}</div>
            ${user.role === 'admin' ? '<a href="admin.html">Admin Dashboard</a>' : ''}
            <a href="maps.html">Open Maps</a>
            <a href="#" data-action="logout">Logout</a>
          </div>
        </div>
      `;
    } else {
      userMenuHtml = `
        <div class="user-menu" id="user-menu">
          <button class="btn-user" id="user-menu-btn" type="button" title="Account" aria-label="Account menu">👤</button>
          <div class="user-menu-dropdown" id="user-menu-dropdown">
            <a href="auth.html#login">Login</a>
            <a href="auth.html#signup">Sign Up</a>
          </div>
        </div>
      `;
    }

    mount.innerHTML = `
      <div class="site-brand">Informal Settlement Mapping and Visualization</div>
      <nav class="site-nav" aria-label="Main">
        ${PAGES.map((p) => `
          <a href="${p.href}" class="${activePage === p.href ? 'active' : ''}">${p.label}</a>
        `).join('')}
      </nav>
      <div class="site-header-actions">
        ${userMenuHtml}
        <button class="btn-theme" id="theme-toggle" type="button" title="Toggle light/dim theme" aria-label="Toggle theme">☀️</button>
      </div>
    `;

    bindUserMenu();
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
