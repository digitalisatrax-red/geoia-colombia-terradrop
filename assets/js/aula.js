/* Aula Geovisor: etapas, comparación tabla/mapa, geovisores nacionales, anatomía y cuestionario */
(async function () {
  const $ = (id) => document.getElementById(id), { esc, fmt, norm } = GEO;
  const title = (s) => String(s).toLowerCase().split(' ').map((w, i) => (w.startsWith('d.c') ? 'D.C.' : i && ['de', 'del', 'la', 'y', 'el'].includes(w) ? w : w.charAt(0).toUpperCase() + w.slice(1))).join(' ');
  let MUN = [], MAP = null;
  try { [MUN, MAP] = await Promise.all([GEO.json('data/municipios.json'), GEO.json('data/mapa_colombia.json')]); } catch (e) { /* las secciones sin datos siguen funcionando */ }

  // ---- 1. etapas ----
  const STAGES = [
    { i: '📡', t: 'Captura', p: 'Sensores, trabajo de campo y registros administrativos producen el dato: imágenes satelitales, catastro, estaciones, encuestas.', q: '¿Qué existe en el territorio?', e: 'IGAC (cartografía y catastro), IDEAM (clima y coberturas) y DANE (veredas y censo).', c: 'bg-blue', img: 'globe' },
    { i: '⬇️', t: 'Descarga', p: 'Portales y servicios REST entregan el dato. TerraDrop los consulta por ti, recorre todas las páginas y filtra al lugar que elegiste.', q: '¿Cómo consigo lo que necesito?', e: 'Nueve capas de un municipio en GeoJSON, o todo en un ZIP.', c: 'bg-yellow', img: 'machine' },
    { i: '🗂', t: 'Capas', p: 'En QGIS o Colab cada archivo es una capa: la ordenas, la simbolizas y la cruzas con otras.', q: '¿Cómo se relacionan estos datos?', e: 'Cruzar veredas con áreas protegidas para saber cuánta vereda queda dentro de una.', c: 'bg-green', img: 'layers' },
    { i: '🗺', t: 'Geovisor', p: 'El visor junta capas, leyenda y herramientas para que cualquier persona consulte sin ser experta en SIG.', q: '¿Qué hay aquí y qué hay al lado?', e: 'Hacer clic en un polígono y leer su atributo; encender y apagar capas; imprimir un mapa.', c: 'bg-purple', img: 'magnifier' },
    { i: '✅', t: 'Decisión', p: 'Se decide con evidencia: ordenar el territorio, conservar, invertir o atender un riesgo.', q: '¿Qué hacemos con esto?', e: 'Priorizar veredas con vías en mal estado dentro de zonas de manejo ambiental.', c: 'bg-pink', img: 'cube' },
  ];
  const pipe = $('pipe'), body = $('pipeBody');
  STAGES.forEach((s, k) => pipe.insertAdjacentHTML('beforeend', `<button role="tab" aria-selected="${k === 3}" data-k="${k}"><span>${s.i}</span>${s.t}</button>`));
  function showStage(k) {
    const s = STAGES[k]; pipe.querySelectorAll('button').forEach((b) => b.setAttribute('aria-selected', +b.dataset.k === k));
    body.innerHTML = `<div><span class="eyebrow">Etapa ${k + 1} de 5</span><h3 style="font-size:2rem">${s.t}</h3><p class="lead" style="font-size:1.05rem">${s.p}</p><p><b>Pregunta que responde:</b> ${s.q}</p><p style="color:var(--ink-2)"><b>En Colombia:</b> ${s.e}</p>${k === 1 ? '<a class="btn dark" href="descargas.html">Abrir TerraDrop</a>' : k === 3 ? '<a class="btn dark" href="colombia-en-mapas.html">Practicar en un visor</a>' : ''}</div><div class="pillar art ${s.c}" style="border:0;padding:0;aspect-ratio:1.4/1;display:grid;place-items:center;border-radius:var(--r-lg)"><img src="assets/img/${s.img}.svg" alt="" aria-hidden="true" style="width:min(260px,70%)"></div>`;
  }
  pipe.addEventListener('click', (e) => { const b = e.target.closest('button'); if (b) showStage(+b.dataset.k); });
  showStage(3);

  // ---- 2. tabla vs mapa ----
  const PICK = ['17001', '63690', '05364', '63272', '91001', '44001', '27001'].filter((c) => MUN.some((m) => m.c === c));
  const sel = $('cmpSel');
  sel.innerHTML = PICK.map((c) => { const m = MUN.find((x) => x.c === c); return `<option value="${c}">${esc(title(m.n))} · ${esc(title(m.dn))}</option>`; }).join('');
  function pathBox(d) { const n = d.match(/-?\d+(?:\.\d+)?/g).map(Number); let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9; for (let i = 0; i < n.length; i += 2) { x0 = Math.min(x0, n[i]); x1 = Math.max(x1, n[i]); y0 = Math.min(y0, n[i + 1]); y1 = Math.max(y1, n[i + 1]); } return [x0, y0, x1, y1]; }
  function compare() {
    const m = MUN.find((x) => x.c === sel.value); if (!m || !MAP) return;
    const rows = [['cod_dane', m.c], ['departamento', title(m.dn)], ['area_km2', fmt(m.a)], ['areas_protegidas', m.ap], ['nombres_areas', (m.na || '—').slice(0, 60) + ((m.na || '').length > 60 ? '…' : '')], ['rios_principales', m.nr || '—'], ['humedales_v3', m.hm]];
    const d = MAP.mun[m.c]; let zoomSvg = '<p style="padding:40px;text-align:center;color:var(--muted)">Este territorio está fuera del mapa continental.</p>';
    if (d) { const [x0, y0, x1, y1] = pathBox(d), pw = Math.max(x1 - x0, 1), ph = Math.max(y1 - y0, 1), pad = Math.max(pw, ph) * .12; zoomSvg = `<svg viewBox="${x0 - pad} ${y0 - pad} ${pw + 2 * pad} ${ph + 2 * pad}" role="img" aria-label="Forma de ${esc(title(m.n))}"><path d="${d}" fill="#ffc93c" stroke="#0d0d12" stroke-width="${Math.max(pw, ph) / 70}" stroke-linejoin="round"/></svg>`; }
    const ctx = Object.values(MAP.dep).filter((x) => x.p).map((x) => `<path d="${x.p}" fill="#e8e2d2" stroke="#fff" stroke-width="3"/>`).join('') + (d ? `<path d="${d}" fill="#ff4d4d" stroke="#0d0d12" stroke-width="5"/>` : '');
    $('cmp').innerHTML = `<div class="box"><h3>Sin visor: una tabla</h3><table><tbody>${rows.map(([a, b]) => `<tr><th scope="row" style="font-family:ui-monospace,monospace;font-weight:500;color:var(--muted)">${a}</th><td>${esc(b)}</td></tr>`).join('')}</tbody></table><p class="hint">¿Es grande o pequeño? ¿Está cerca del mar? ¿Cerca de otro municipio protegido? La tabla no lo dice.</p></div>
      <div class="box"><h3>Con visor: un mapa</h3><div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;align-items:center"><svg viewBox="0 0 ${MAP.w} ${MAP.h}" style="height:280px" role="img" aria-label="Ubicación en Colombia">${ctx}</svg>${zoomSvg}</div><p class="hint">En un vistazo: dónde está, qué forma tiene y con quién limita.</p></div>`;
  }
  sel.addEventListener('change', compare); compare();

  // ---- 3. geovisores ----
  const VIEWERS = [
    { n: 'Colombia en Mapas', o: 'IGAC', u: 'https://www.colombiaenmapas.gov.co/', ic: '🧭', bg: 'bg-yellow', q: '¿Qué cartografía, catastro y suelos hay en este lugar?', w: 'Cartografía básica, catastro, agrología, imágenes y geodesia en un solo visor. Es el que practicas en este aula.', t: 'colombia-en-mapas.html' },
    { n: 'Visualizador IDEAM', o: 'IDEAM', u: 'https://visualizador.ideam.gov.co/', ic: '🌦', bg: 'bg-blue', q: '¿Qué cobertura, clima y estado ambiental tiene?', w: 'Coberturas de la tierra, clima, hidrología y otros temas ambientales. De aquí sale la capa CLC 2024 de TerraDrop.' },
    { n: 'RUNAP', o: 'Parques Nacionales Naturales', u: 'https://runap.parquesnacionales.gov.co/', ic: '🌿', bg: 'bg-green', q: '¿Qué áreas protegidas hay y de qué categoría?', w: 'El registro oficial de áreas protegidas: nombre, categoría, estado y ámbito de gestión.' },
    { n: 'Geoportal DANE', o: 'DANE', u: 'https://geoportal.dane.gov.co/', ic: '📊', bg: 'bg-purple', q: '¿Cuántas personas, viviendas y veredas hay y dónde?', w: 'Marco geoestadístico (departamentos, municipios, veredas) y visores de estadísticas del censo.' },
  ];
  $('viewers').innerHTML = VIEWERS.map((v) => `<article class="card viewer-card reveal"><div class="top"><div class="dot ${v.bg}" aria-hidden="true">${v.ic}</div><div><h3 style="margin:0">${v.n}</h3><small style="color:var(--muted)">${v.o}</small></div></div><p style="margin:6px 0"><b>Pregunta clave:</b> ${v.q}</p><p style="color:var(--ink-2)">${v.w}</p><div style="display:flex;gap:10px;flex-wrap:wrap">${v.t ? `<a class="btn sm dark" href="${v.t}">Aprender paso a paso</a>` : ''}<a class="btn sm" href="${v.u}" target="_blank" rel="noopener">Abrir visor oficial ↗</a></div></article>`).join('');
  document.querySelectorAll('#viewers .reveal').forEach((el) => setTimeout(() => el.classList.add('in'), 60));

  // ---- 4. anatomía ----
  if (MAP) $('anatBg').innerHTML = `<rect width="800" height="500" fill="#0b2a3a"/><g transform="translate(250,20) scale(.27)">${Object.values(MAP.dep).filter((x) => x.p).map((x) => `<path d="${x.p}" fill="#1f6f6a" stroke="#0b2a3a" stroke-width="5"/>`).join('')}</g>`;
  $('anat').insertAdjacentHTML('beforeend', '<div class="vcoord" data-k="leyenda" style="left:12px;right:auto;bottom:62px;cursor:pointer;display:block;font-family:var(--body)"><span style="display:inline-block;width:10px;height:10px;background:#27c98f;border-radius:50%;margin-right:6px"></span>Áreas protegidas &nbsp;<span style="display:inline-block;width:10px;height:10px;background:#ff4d4d;border-radius:50%;margin:0 6px 0 8px"></span>Vías</div>');
  const ANAT = {
    barra: ['Barra de herramientas', 'Aquí viven las acciones: explorar el catálogo, filtrar, consultar coordenadas, medir, importar datos, imprimir.', 'Pregúntate: ¿qué puedo hacer con el mapa?'],
    panel: ['Panel lateral', 'Despliega información de contexto y la lista de capas activas. Se abre desde el borde del mapa.', 'Pregúntate: ¿qué capas están encendidas ahora?'],
    mapa: ['Lienzo del mapa', 'Arrastra para moverte, usa la rueda para acercar y haz clic para consultar lo que hay bajo el puntero.', 'Pregúntate: ¿qué hay exactamente en este punto?'],
    zoom: ['Controles de zoom', 'Acercan y alejan la vista. También puedes usar la rueda del ratón o el doble clic.', 'Pregúntate: ¿qué tan cerca necesito ver?'],
    coord: ['Coordenadas y escala', 'Indican dónde está el puntero y qué sistema de referencia se usa (por ejemplo EPSG:9377, origen nacional), y cuánto mide la escala.', 'Pregúntate: ¿en qué sistema están mis datos?'],
    leyenda: ['Leyenda', 'Traduce colores y símbolos a significados. Sin leyenda, un mapa es solo una imagen bonita.', 'Pregúntate: ¿qué significa este color?'],
  };
  function anat(k) { const a = ANAT[k]; $('aN').textContent = 'Pieza ' + (Object.keys(ANAT).indexOf(k) + 1) + ' de 6'; $('aT').textContent = a[0]; $('aP').textContent = a[1]; $('aQ').textContent = a[2]; $('anat').querySelectorAll('[data-k]').forEach((el) => el.classList.toggle('active', el.dataset.k === k)); }
  $('anat').addEventListener('click', (e) => { const t = e.target.closest('[data-k]'); if (t) anat(t.dataset.k); });
  anat('barra');

  // ---- 5. cuestionario ----
  const QZ = [
    { q: 'Tienes una tabla con 1.121 municipios y su porcentaje de bosque. ¿Qué pregunta responde mejor un geovisor?', o: ['¿Cuál es el promedio nacional?', '¿Dónde están los municipios con menos bosque y qué hay a su alrededor?', '¿Cuántas columnas tiene la tabla?'], a: 1, w: 'Un visor responde preguntas de ubicación y vecindad, que una tabla no muestra.' },
    { q: '¿Qué pieza del visor te dice qué significa cada color del mapa?', o: ['La barra de coordenadas', 'Los controles de zoom', 'La leyenda'], a: 2, w: 'La leyenda traduce colores y símbolos a significados.' },
    { q: 'Descargaste las vías y las áreas protegidas de tu municipio. ¿Cuál es el paso lógico siguiente?', o: ['Abrirlas como capas en QGIS o en un visor y cruzarlas', 'Borrarlas para ahorrar espacio', 'Pasarlas a Excel para ver el mapa'], a: 0, w: 'Cada archivo es una capa; el valor aparece al superponerlas y consultarlas.' },
  ];
  let score = 0, answered = 0;
  $('quiz').innerHTML = QZ.map((z, i) => `<div class="quizq" data-i="${i}"><h3>${i + 1}. ${z.q}</h3><div class="opts">${z.o.map((o, j) => `<button data-j="${j}">${o}</button>`).join('')}</div><p class="hint" hidden></p></div>`).join('');
  $('quiz').addEventListener('click', (e) => {
    const b = e.target.closest('button'); if (!b) return; const box = b.closest('.quizq'); if (box.dataset.done) return;
    const z = QZ[+box.dataset.i], j = +b.dataset.j; box.dataset.done = 1; answered++;
    box.querySelectorAll('button').forEach((x, k) => { if (k === z.a) x.classList.add('good'); else if (x === b) x.classList.add('bad'); });
    if (j === z.a) score++; const h = box.querySelector('.hint'); h.hidden = false; h.textContent = (j === z.a ? '¡Correcto! ' : 'Casi. ') + z.w;
    if (answered === QZ.length) $('quizScore').textContent = `Resultado: ${score} de ${QZ.length}. ${score === QZ.length ? '¡Listo para el tutorial!' : 'Repasa la anatomía y vuelve a intentarlo.'}`;
  });
})();
