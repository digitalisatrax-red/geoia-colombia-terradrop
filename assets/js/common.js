/* GeoIA Colombia · utilidades compartidas: navegación, pie, avisos, helpers */
(function () {
  const PAGES = [
    ['index.html', 'Inicio', 'home'],
    ['descargas.html', 'TerraDrop', 'descargas'],
    ['aula.html', 'Aula', 'aula'],
    ['colombia-en-mapas.html', 'Colombia en Mapas', 'tour'],
    ['fuentes.html', 'Fuentes', 'fuentes'],
  ];
  const cur = document.body.dataset.page;

  const announce = `<div class="announce">Nuevo · <b>Modo Aula</b>: cada estudiante recibe su municipio, descarga sus capas y aprende a leer un geovisor. <a href="descargas.html?modo=aula">Probar ahora →</a></div>`;
  const nav = `<header class="nav" id="nav"><div class="wrap">
    <a class="brand" href="index.html" aria-label="GeoIA Colombia, inicio"><i></i>GeoIA Colombia</a>
    <ul>${PAGES.map(([h, t, k]) => `<li><a href="${h}" ${k === cur ? 'aria-current="page"' : ''}>${t}</a></li>`).join('')}</ul>
    <div class="cta"><a class="btn sm" href="descargas.html?modo=aula">Modo Aula</a><a class="btn sm dark" href="descargas.html">Descargar datos</a></div>
    <button class="burger" aria-label="Abrir menú" aria-expanded="false">☰</button>
  </div></header>`;
  const footer = `<footer><div class="wrap"><div class="cols">
    <div><a class="brand" href="index.html"><i></i>GeoIA Colombia</a><p style="margin-top:14px;color:var(--ink-2);max-width:340px">Gestor de descarga de datos territoriales para aprender, enseñar y trabajar con geovisores. Datos abiertos oficiales, asistente local y práctica guiada.</p></div>
    <div><h4>Producto</h4><a href="descargas.html">TerraDrop</a><a href="descargas.html?modo=aula">Modo Aula</a><a href="fuentes.html">Fuentes y calidad</a></div>
    <div><h4>Aprende</h4><a href="aula.html">Por qué un geovisor</a><a href="colombia-en-mapas.html">Colombia en Mapas, clic a clic</a></div>
    <div><h4>Fuentes oficiales</h4><a href="https://www.colombiaenmapas.gov.co/" target="_blank" rel="noopener">Colombia en Mapas (IGAC)</a><a href="https://visualizador.ideam.gov.co/" target="_blank" rel="noopener">Visualizador IDEAM</a><a href="https://runap.parquesnacionales.gov.co/" target="_blank" rel="noopener">RUNAP</a></div>
  </div><small>Proyecto educativo independiente. Las descargas se hacen directamente desde los servicios de las entidades; GeoIA Colombia no almacena tus datos. Las réplicas de visores son didácticas y no oficiales.</small></div></footer>`;

  document.body.insertAdjacentHTML('afterbegin', `<a class="skip" href="#main">Saltar al contenido</a>${announce}${nav}`);
  document.body.insertAdjacentHTML('beforeend', footer + '<div class="toast" id="toast" role="status" aria-live="polite"></div>');

  const navEl = document.getElementById('nav');
  addEventListener('scroll', () => navEl.classList.toggle('scrolled', scrollY > 8), { passive: true });
  navEl.querySelector('.burger').addEventListener('click', (e) => {
    const open = navEl.classList.toggle('open');
    e.currentTarget.setAttribute('aria-expanded', open);
  });

  // helpers globales
  window.GEO = {
    norm: (s) => String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9ñ ]+/g, ' ').replace(/\s+/g, ' ').trim(),
    toast(msg) {
      const t = document.getElementById('toast');
      t.textContent = msg; t.classList.add('show');
      clearTimeout(t._h); t._h = setTimeout(() => t.classList.remove('show'), 2600);
    },
    copy(text) {
      const done = () => GEO.toast('Copiado al portapapeles');
      if (navigator.clipboard) navigator.clipboard.writeText(text).then(done, done); else done();
    },
    store: {
      get(k, d) { try { const v = localStorage.getItem('geoia:' + k); return v ? JSON.parse(v) : d; } catch (e) { return d; } },
      set(k, v) { try { localStorage.setItem('geoia:' + k, JSON.stringify(v)); } catch (e) { /* sin almacenamiento */ } },
    },
    async json(path) {
      try { const r = await fetch(path); if (!r.ok) throw new Error(path + ' ' + r.status); return await r.json(); }
      catch (e) { /* abierto con doble clic (file://): se leen las copias .js de data/ */
        window.__GEO_DATA = window.__GEO_DATA || {};
        if (!window.__GEO_DATA[path]) await new Promise((ok, no) => { const sc = document.createElement('script'); sc.src = path.replace(/\.json$/, '.js'); sc.onload = ok; sc.onerror = () => no(e); document.head.appendChild(sc); });
        if (window.__GEO_DATA[path]) return window.__GEO_DATA[path]; throw e;
      }
    },
    esc: (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])),
    hash(str) { let h = 2166136261; for (let i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; },
    fmt: (n) => new Intl.NumberFormat('es-CO').format(n),
  };

  // aparición suave
  const io = 'IntersectionObserver' in window ? new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { threshold: .12 }) : null;
  document.querySelectorAll('.reveal').forEach((el) => (io ? io.observe(el) : el.classList.add('in')));

  // botones de copiar comando
  document.querySelectorAll('[data-copy]').forEach((b) => b.addEventListener('click', () => GEO.copy(b.dataset.copy)));
})();
