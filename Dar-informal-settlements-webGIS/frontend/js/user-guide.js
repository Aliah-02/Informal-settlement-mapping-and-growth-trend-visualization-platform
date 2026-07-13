/**
 * Bilingual user guide content (English & Kiswahili).
 */
const UserGuide = (() => {
  const CONTENT = {
    en: {
      title: 'How to Use the Platform',
      sections: [
        {
          title: '1. Getting Started',
          steps: [
            'Open the Home page to see an overview, growth charts, and visitor statistics.',
            'Click MAPS in the navigation bar to open the interactive WebGIS map.',
            'Use the theme button (☀️/🌙) in the header to switch between light and dim modes.',
          ],
        },
        {
          title: '2. Exploring the Map',
          steps: [
            'On the Maps page, drag the year slider (2005–2026) to view settlement layers for each analysis year.',
            'Click settlement polygons to see ISI score, probability level, area, and population proxy.',
            'Use the fullscreen button (⛶) on the map panel to expand the map view.',
            'Enable Change Detection Mode to compare two years and highlight new, expanded, or contracted settlements.',
          ],
        },
        {
          title: '3. Statistics & Reports',
          steps: [
            'Visit the Statistics page for ward-level trends and district growth summaries.',
            'On the Maps dashboard, click "CSV Report" to download the growth trend report.',
            'After change detection, use "Download Change CSV" for a detailed change report.',
          ],
        },
        {
          title: '4. Account & Admin',
          steps: [
            'Click LOGIN / SIGN UP to create a user account or sign in.',
            'Registered users can download reports; downloads are tracked for platform analytics.',
            'Administrators see the Admin Dashboard with live users, total downloads, and who downloaded reports.',
          ],
        },
      ],
    },
    sw: {
      title: 'Jinsi ya Kutumia Jukwaa',
      sections: [
        {
          title: '1. Kuanza',
          steps: [
            'Fungua ukurasa wa Home kuona muhtasari, chati za ukuaji, na takwimu za wageni.',
            'Bofya MAPS kwenye menyu kuufungua ramani ya WebGIS.',
            'Tumia kitufe cha mandhari (☀️/🌙) kubadilisha hali ya mwanga au giza.',
          ],
        },
        {
          title: '2. Kuchunguza Ramani',
          steps: [
            'Kwenye ukurasa wa Maps, songesha kislipta cha mwaka (2005–2026) kuona tabaka la makazi kwa kila mwaka.',
            'Bofya poligoni za makazi kuona alama ya ISI, kiwango cha uwezekano, eneo, na makadirio ya idadi ya watu.',
            'Tumia kitufe cha skrini nzima (⛶) kwenye paneli ya ramani kupanua mwonekano wa ramani.',
            'Washa Change Detection Mode kulinganisha miaka miwili na kuonyesha makazi mapya, yaliyoongezeka, au kupungua.',
          ],
        },
        {
          title: '3. Takwimu na Ripoti',
          steps: [
            'Tembelea ukurasa wa Statistics kwa mienendo ya kata na muhtasari wa ukuaji wa wilaya.',
            'Kwenye dashibodi ya Maps, bofya "CSV Report" kupakua ripoti ya mwenendo wa ukuaji.',
            'Baada ya change detection, tumia "Download Change CSV" kwa ripoti ya mabadiliko.',
          ],
        },
        {
          title: '4. Akaunti na Msimamizi',
          steps: [
            'Bofya LOGIN / SIGN UP kuunda akaunti au kuingia.',
            'Watumiaji waliosajiliwa wanaweza kupakua ripoti; upakuaji unafuatiliwa kwa takwimu za jukwaa.',
            'Wasimamizi wanaona Admin Dashboard wenye watumiaji hai, jumla ya upakuaji, na nani aliyepakua ripoti.',
          ],
        },
      ],
    },
  };

  function render(lang) {
    const data = CONTENT[lang] || CONTENT.en;
    const mount = document.getElementById('guide-content');
    if (!mount) return;
    mount.innerHTML = `
      <p style="margin-bottom:1rem;color:var(--text-muted);">${lang === 'sw' ? 'Mwongozo kamili wa kutumia tovuti.' : 'Complete instructions for using the website.'}</p>
      ${data.sections.map((s) => `
        <section class="guide-section">
          <h3>${s.title}</h3>
          <ol>${s.steps.map((step) => `<li>${step}</li>`).join('')}</ol>
        </section>
      `).join('')}
    `;
  }

  function init() {
    let current = 'en';
    render(current);

    document.getElementById('btn-en')?.addEventListener('click', () => {
      current = 'en';
      document.getElementById('btn-en').classList.add('active');
      document.getElementById('btn-sw').classList.remove('active');
      render(current);
    });

    document.getElementById('btn-sw')?.addEventListener('click', () => {
      current = 'sw';
      document.getElementById('btn-sw').classList.add('active');
      document.getElementById('btn-en').classList.remove('active');
      render(current);
    });
  }

  return { init, render, CONTENT };
})();

window.UserGuide = UserGuide;
