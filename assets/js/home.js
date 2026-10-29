/* Inicio: pestañas de capas con mapas generados desde data/mapa_colombia.json y chips del asistente */
(async function () {
  const TABS = [
    { id: 'limites', t: 'Límites y veredas', h: 'Tu lugar, con sus veredas', color: '#ffc93c', deps: ['17'], tags: ['Municipio · IDEAM', 'Veredas DANE 2024', 'Código DANE'],
      p: 'Elige un departamento, luego un municipio y, si quieres, una sola vereda. Descargas el polígono oficial y todas las veredas que lo componen, con sus códigos DANE.', img: 'magnifier' },
    { id: 'runap', t: 'Áreas protegidas', h: 'Qué está protegido dentro del límite', color: '#27c98f', deps: ['27', '52', '19', '91'], tags: ['RUNAP', 'MinAmbiente', 'Nombre y categoría'],
      p: 'El Registro Único Nacional de Áreas Protegidas se filtra al polígono de tu municipio. Cada área trae categoría, estado, ámbito de gestión y hectáreas.', img: 'globe' },
    { id: 'agua', t: 'Agua', h: 'Ríos y drenajes del territorio', color: '#2f6ff0', deps: ['05', '13', '23', '70'], tags: ['Drenajes', 'Ríos principales'],
      p: 'Drenajes de la capa de hidrografía y los ríos principales de Colombia. Útil para ver cuencas, rondas y hasta dónde llega el agua.', img: 'cube' },
    { id: 'vias', t: 'Vías', h: 'Cómo se llega a cada vereda', color: '#ff6b5e', deps: ['25', '15', '68', '54'], tags: ['Pavimentadas', 'Sin pavimentar', 'Transitables en tiempo seco'],
      p: 'Tres capas del IGAC: vías pavimentadas, sin pavimentar y transitables en tiempo seco. Perfectas para accesibilidad y logística.', img: 'machine' },
    { id: 'clc', t: 'Coberturas CLC 2024', h: 'Qué hay sobre el suelo', color: '#8b6cf0', deps: ['50', '85', '99', '94'], tags: ['Corine Land Cover', 'Escala 1:100.000', 'Niveles 1 a 6'],
      p: 'La cobertura de la tierra del IDEAM, periodo 2024, con leyenda por niveles. Bosques, pastos, cultivos, zonas urbanas y cuerpos de agua.', img: 'layers' },
  ];
  let M = null;
  try { M = await GEO.json('data/mapa_colombia.json'); } catch (e) { /* sin mapa: las pestañas siguen funcionando */ }

  function map(color, deps) {
    if (!M) return '';
    const base = Object.entries(M.dep).filter(([, v]) => v.p).map(([k, v]) => `<path d="${v.p}" fill="${deps.includes(k) ? color : '#e9e4d6'}" stroke="#fff" stroke-width="2.2" stroke-linejoin="round"/>`).join('');
    return `<svg viewBox="-10 -10 ${M.w + 20} ${M.h + 20}" role="img" aria-label="Mapa de Colombia con departamentos destacados">${base}</svg>`;
  }

  const tabs = document.getElementById('tabs'), panels = document.getElementById('tabpanels');
  TABS.forEach((t, i) => {
    tabs.insertAdjacentHTML('beforeend', `<button class="tab" role="tab" id="tab-${t.id}" aria-controls="pn-${t.id}" aria-selected="${i === 0}">${t.t}</button>`);
    panels.insertAdjacentHTML('beforeend', `<div class="tabpanel" role="tabpanel" id="pn-${t.id}" aria-labelledby="tab-${t.id}" ${i ? 'hidden' : ''}>
      <div><h3 style="font-size:2rem">${t.h}</h3><p class="lead" style="font-size:1.05rem">${t.p}</p><div>${t.tags.map((x) => `<span class="tag">${x}</span>`).join('')}</div><a class="btn dark" style="margin-top:18px" href="descargas.html">Descargar esta capa</a></div>
      <div class="art" style="position:relative">${map(t.color, t.deps)}<img src="assets/img/${t.img}.svg" alt="" aria-hidden="true" style="position:absolute;right:6%;bottom:4%;width:34%;height:auto"></div></div>`);
  });
  tabs.addEventListener('click', (e) => {
    const b = e.target.closest('.tab'); if (!b) return;
    tabs.querySelectorAll('.tab').forEach((x) => x.setAttribute('aria-selected', x === b));
    panels.querySelectorAll('.tabpanel').forEach((p) => (p.hidden = p.id !== b.getAttribute('aria-controls')));
  });
  tabs.addEventListener('keydown', (e) => {
    if (!['ArrowRight', 'ArrowLeft'].includes(e.key)) return;
    const all = [...tabs.querySelectorAll('.tab')], i = all.indexOf(document.activeElement);
    if (i < 0) return;
    const n = all[(i + (e.key === 'ArrowRight' ? 1 : all.length - 1)) % all.length]; n.focus(); n.click();
  });

  const EX = ['Veredas y coberturas de Filandia', 'Todo de Salento, Quindío', 'Vías y ríos de Jardín, Antioquia', 'Áreas protegidas de Manizales', 'Un municipio al azar con áreas protegidas'];
  const chips = document.getElementById('chips');
  EX.forEach((x) => chips.insertAdjacentHTML('beforeend', `<button class="chip-btn" type="button">${x}</button>`));
  chips.addEventListener('click', (e) => {
    const b = e.target.closest('.chip-btn'); if (!b) return;
    document.getElementById('askInput').value = b.textContent;
    document.getElementById('askForm').submit();
  });
})();
