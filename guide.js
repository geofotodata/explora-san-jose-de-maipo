/* Shared navigation and progressive directory filtering; no live access claims. */
(() => {
  'use strict';
  const menu = document.querySelector('#guide-menu');
  const nav = document.querySelector('#guide-nav');
  menu?.addEventListener('click', () => {
    const open = menu.getAttribute('aria-expanded') !== 'true';
    menu.setAttribute('aria-expanded', String(open)); nav.classList.toggle('open', open);
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && nav?.classList.contains('open')) {
      nav.classList.remove('open'); menu.setAttribute('aria-expanded', 'false'); menu.focus();
    }
  });
  const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  const search = document.querySelector('#directory-search');
  if (search) {
    const sector = document.querySelector('#directory-sector');
    const kind = document.querySelector('#directory-kind');
    const cards = [...document.querySelectorAll('.directory-card')];
    search.value = new URLSearchParams(location.search).get('q') || '';
    const filter = () => {
      let count = 0;
      for (const card of cards) {
        const show = normalize(card.dataset.name).includes(normalize(search.value.trim())) && (!sector.value || card.dataset.sector === sector.value) && (!kind.value || card.dataset.kind === kind.value);
        card.hidden = !show; if (show) count++;
      }
      document.querySelector('#directory-count').textContent = `${count} de ${cards.length} lugares`;
      document.querySelector('#directory-empty').hidden = count !== 0;
    };
    search.addEventListener('input', filter); sector.addEventListener('change', filter); kind.addEventListener('change', filter); filter();
  }
  // Preserve old bookmarked anchors after splitting the original single page.
  const oldRoutes = {mapa:'mapa.html#mapa',condiciones:'condiciones.html#condiciones',explorar:'explora.html',rutas:'planifica.html#rutas',planifica:'planifica.html#planifica',alertas:'planifica.html#alertas',zoit:'naturaleza.html#zoit'};
  if (location.pathname.endsWith('/') || location.pathname.endsWith('/index.html')) {
    const route = oldRoutes[location.hash.slice(1)]; if (route) location.replace(route);
  }
  if ('serviceWorker' in navigator) {
    const root = new URL('.', document.currentScript?.src || document.querySelector('script[src$="guide.js"]').src);
    navigator.serviceWorker.register(new URL('service-worker.js', root)).catch(error => console.warn('No se pudo activar el modo sin conexión', error));
  }
})();
