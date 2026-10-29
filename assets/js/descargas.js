/* TerraDrop · interfaz del gestor de descargas (Municipio / Modo Aula) */
(async function () {
  const $ = (id) => document.getElementById(id);
  const { norm, esc, fmt, hash, store, toast } = GEO;
  const SMALL = ['de', 'del', 'la', 'las', 'los', 'y', 'e', 'el'];
  const title = (s) => String(s).toLowerCase().split(' ').map((w, i) => (w.startsWith('d.c') ? 'D.C.' : i && SMALL.includes(w) ? w : w.charAt(0).toUpperCase() + w.slice(1))).join(' ');
  const slug = (s) => norm(s).replace(/ /g, '-');

  let MUN, MAP;
  try { [MUN, MAP] = await Promise.all([GEO.json('data/municipios.json'), GEO.json('data/mapa_colombia.json')]); }
  catch (e) {
    $('say').innerHTML = '<b>No pude cargar los datos locales.</b> Abre el sitio desde un servidor (GitHub Pages, o en tu equipo: <code>python -m http.server</code>) en lugar de abrir el archivo directamente.';
    return;
  }
  const byCode = Object.fromEntries(MUN.map((m) => [m.c, m]));
  const P = MAP.proj;
  const DEPS = [...new Map(MUN.map((m) => [m.d, m.dn])).entries()].map(([d, dn]) => ({ d, dn })).sort((a, b) => norm(a.dn).localeCompare(norm(b.dn)));

  // ---------- estado ----------
  const S = { mode: 'municipio', mun: null, ver: null, on: new Set(LAYERS.map((l) => l.id)), res: new Map(), status: {}, running: false, ctrl: null, boundary: null, assign: store.get('assign', null), attempt: 0 };

  // ---------- selectores ----------
  const selDep = $('selDep'), selMun = $('selMun'), selVer = $('selVer'), finder = $('finder');
  selDep.innerHTML = '<option value="">Elige un departamento…</option>' + DEPS.map((x) => `<option value="${x.d}">${esc(title(x.dn))} (${MUN.filter((m) => m.d === x.d).length})</option>`).join('');
  $('finderList').innerHTML = MUN.map((m) => `<option value="${esc(title(m.n))} · ${esc(title(m.dn))}"></option>`).join('');
  $('drawScope').innerHTML = '<option value="">Todo el país</option>' + DEPS.map((x) => `<option value="${x.d}">${esc(title(x.dn))}</option>`).join('');
  $('apCount').textContent = MUN.filter((m) => m.ap > 0).length + ' de ' + MUN.length;

  function fillMun(d, keep) {
    const list = MUN.filter((m) => m.d === d);
    selMun.innerHTML = '<option value="">Elige un municipio…</option>' + list.map((m) => `<option value="${m.c}">${esc(title(m.n))}${m.ap ? ' ★' : ''}</option>`).join('');
    selMun.disabled = !d; if (keep) selMun.value = keep;
  }
  selDep.addEventListener('change', () => { fillMun(selDep.value); clearSel(); $('pickHint').textContent = selDep.value ? 'Departamento activo: ya puedes elegir cualquiera de sus municipios (★ = tiene áreas protegidas).' : ''; });
  selMun.addEventListener('change', () => selectMun(selMun.value));
  selVer.addEventListener('change', () => {
    S.ver = selVer.value ? { cod: selVer.value, nom: selVer.selectedOptions[0].textContent } : null;
    resetResults(); updateRun(); fitSel();
  });
  function onFinder() {
    const v = finder.value.trim(); if (!v) return;
    const exact = MUN.find((m) => `${title(m.n)} · ${title(m.dn)}` === v);
    if (exact) { selectMun(exact.c); return; }
  }
  finder.addEventListener('change', onFinder);
  finder.addEventListener('keydown', (e) => {
    if (e.key !== 'Enter') return; e.preventDefault();
    const n = norm(finder.value); const hit = MUN.find((m) => norm(m.n).startsWith(n) || norm(m.n.split(',')[0]) === n);
    if (hit) selectMun(hit.c); else toast('No encontré ese municipio');
  });

  function clearSel() { S.mun = null; S.ver = null; selVer.innerHTML = '<option>Primero elige un municipio</option>'; selVer.disabled = true; resetResults(); updateRun(); draw(); }

  async function selectMun(code, opts = {}) {
    const m = byCode[code]; if (!m) return;
    S.mun = m; S.ver = null;
    selDep.value = m.d; fillMun(m.d, m.c); selMun.value = m.c; finder.value = '';
    resetResults(); updateRun();
    $('pickHint').innerHTML = `<b>${esc(title(m.n))}</b> · ${esc(title(m.dn))} · ${fmt(Math.round(m.a))} km² · ${m.ap ? m.ap + ' área(s) protegida(s)' : 'sin áreas protegidas en el índice'}`;
    S.live = null; fitSel(); draw();
    GEOQ.limitPreview(m.c).then((g) => { if (g && S.mun === m) { const pth = new Path2D(); GEOQ.polygonsOf(g).forEach((pl) => pl.forEach((r) => { r.forEach((c, i) => { const [x, y] = w(c[0], c[1]); i ? pth.lineTo(x, y) : pth.moveTo(x, y); }); pth.closePath(); })); S.live = { code: m.c, p: pth, g }; draw(); } }).catch(() => {});
    selVer.disabled = true; selVer.innerHTML = '<option>Cargando veredas…</option>';
    try {
      const vs = await GEOQ.listVeredas(m.c);
      if (S.mun !== m) return;
      selVer.innerHTML = `<option value="">Todas las veredas (${vs.length})</option>` + vs.map((v) => `<option value="${esc(v.cod)}">${esc(title(v.nom))}</option>`).join('');
      selVer.disabled = !vs.length;
      if (opts.ver) { selVer.value = opts.ver; selVer.dispatchEvent(new Event('change')); }
    } catch (e) { selVer.innerHTML = '<option value="">No se pudieron cargar las veredas ahora</option>'; selVer.disabled = true; }
    refreshRoute();
  }

  // ---------- capas ----------
  function resetResults() { S.res.clear(); S.status = {}; S.boundary = null; $('bar').style.width = '0'; $('zipBtn').disabled = true; $('doneBox').hidden = true; renderLayers(); }
  function renderLayers() {
    $('layerList').innerHTML = LAYERS.map((l) => {
      const st = S.status[l.id], r = S.res.get(l.id);
      let stat = '<span class="stat">en espera</span>';
      if (st === 'run') stat = `<span class="stat run" id="cnt-${l.id}">consultando…</span>`;
      if (st === 'ok') stat = `<span class="stat ok">${fmt(r.count)} · ${r.bytes.length > 1048576 ? (r.bytes.length / 1048576).toFixed(1) + ' MB' : Math.max(1, Math.round(r.bytes.length / 1024)) + ' KB'}</span>`;
      if (st && st.startsWith('err')) stat = `<span class="stat err" title="${esc(st.slice(4))}">error</span>`;
      const dl = st === 'ok' ? `<button class="btn sm ghost" data-dl="${l.id}" aria-label="Descargar ${esc(l.name)}">⬇</button>` : (st && st.startsWith('err') ? `<button class="btn sm ghost" data-retry="${l.id}">↻</button>` : '');
      return `<li class="${S.on.has(l.id) ? 'on' : ''}"><input type="checkbox" id="ck-${l.id}" ${S.on.has(l.id) ? 'checked' : ''} ${S.running ? 'disabled' : ''} aria-label="${esc(l.name)}"><span class="sw" style="background:${l.color}"></span><label class="nm" for="ck-${l.id}">${esc(l.name)}<small>${esc(l.small)}</small></label><span class="act">${dl}</span><span class="st">${stat}</span></li>`;
    }).join('');
    updateRun(); renderLegend();
  }
  $('layerList').addEventListener('change', (e) => {
    const id = e.target.id.replace('ck-', ''); e.target.checked ? S.on.add(id) : S.on.delete(id); renderLayers();
  });
  $('layerList').addEventListener('click', (e) => {
    const dl = e.target.closest('[data-dl]'); if (dl) return saveLayer(dl.dataset.dl);
    const rt = e.target.closest('[data-retry]'); if (rt) return retryLayer(rt.dataset.retry);
  });
  $('allBtn').onclick = () => { LAYERS.forEach((l) => S.on.add(l.id)); renderLayers(); };
  $('noneBtn').onclick = () => { S.on.clear(); renderLayers(); };

  function fileName(l) { return `${S.mun.c}_${slug(S.mun.n)}${S.ver ? '_v' + S.ver.cod : ''}_${l.id}.geojson`; }
  function saveLayer(id) { const l = LAYERS.find((x) => x.id === id), r = S.res.get(id); if (!r) return; GEOQ.saveBlob(new Blob([r.bytes], { type: 'application/geo+json' }), fileName(l)); markStep(2); }

  function updateRun() {
    const ok = !!S.mun && S.on.size > 0 && !S.running;
    $('runBtn').disabled = !ok; $('stopBtn').hidden = !S.running;
    $('runHint').textContent = !S.mun ? 'Elige un municipio para activar la descarga.' : S.running ? 'Trabajando… puedes seguir mirando el mapa.' : `${S.on.size} capa(s) seleccionada(s) para ${title(S.mun.n)}${S.ver ? ' · ' + title(S.ver.nom) : ''}.`;
  }

  // ---------- ejecución ----------
  const enc = new TextEncoder();
  async function doLayer(l, sig) {
    S.status[l.id] = 'run'; renderLayers();
    try {
      let fc;
      if (l.id === 'municipio' && !S.ver && S.boundary && S.boundary.fc) fc = S.boundary.fc;
      else fc = await GEOQ.query(l, { mun: S.mun, ver: S.ver, geom: S.boundary && S.boundary.geom }, (n) => { const el = $('cnt-' + l.id); if (el) el.textContent = fmt(n) + '…'; }, sig);
      const bytes = enc.encode(JSON.stringify(fc));
      S.res.set(l.id, { count: fc.features.length, bytes, items: buildItems(l, fc), note: fc.metadata && fc.metadata.nota });
      S.status[l.id] = 'ok';
    } catch (e) { S.status[l.id] = 'err:' + (e.message || 'fallo'); }
    renderLayers(); draw();
  }
  async function run() {
    if (!S.mun || S.running) return;
    S.ctrl = new AbortController(); const sig = S.ctrl.signal; S.running = true; S.res.clear(); S.status = {}; S.boundary = null; renderLayers();
    $('doneBox').hidden = true;
    say('Delimitando el territorio…');
    const scope = { mun: S.mun, ver: S.ver, geom: null };
    let netDown = false;
    try { S.boundary = await GEOQ.boundary(scope, sig); } catch (e) { S.boundary = null; netDown = /Sin conexión/.test(e.message || ''); }
    if (netDown) {
      S.running = false; S.ctrl = null; LAYERS.filter((l) => S.on.has(l.id)).forEach((l) => (S.status[l.id] = 'err:Sin conexión con el servicio')); renderLayers(); updateRun();
      $('runHint').innerHTML = '<b style="color:#d6336c">Sin conexión con los servicios oficiales.</b> Abre el sitio desde GitHub Pages o con doble clic en index.html; dentro de una vista previa incrustada no funciona.';
      toast('Sin conexión con los servicios oficiales');
      say('<b>No hay conexión con los servicios oficiales desde esta página.</b> Si la abriste dentro de una vista previa incrustada, ábrela desde GitHub Pages o en tu computador (doble clic en index.html). Si no, revisa tu conexión e inténtalo de nuevo.');
      return;
    }
    if (!S.boundary || !S.boundary.geom) {
      const b = S.mun.bb; S.boundary = { fc: null, geom: { type: 'Polygon', coordinates: [[[b[0], b[1]], [b[2], b[1]], [b[2], b[3]], [b[0], b[3]], [b[0], b[1]]]] } };
      say('No encontré el polígono oficial en el servicio; uso la envolvente del municipio como filtro.');
    } else fitGeom(S.boundary.geom);
    draw();
    const todo = LAYERS.filter((l) => S.on.has(l.id)); let i = 0, done = 0;
    todo.forEach((l) => (S.status[l.id] = 'wait')); renderLayers();
    const worker = async () => { while (i < todo.length && !sig.aborted) { const l = todo[i++]; await doLayer(l, sig); done++; $('bar').style.width = Math.round((done / todo.length) * 100) + '%'; } };
    await Promise.all([worker(), worker()]);
    S.running = false; S.ctrl = null;
    const ok = [...S.res.keys()].length, bad = todo.filter((l) => (S.status[l.id] || '').startsWith('err')).length;
    renderLayers();
    $('zipBtn').disabled = !ok; $('doneBox').hidden = !ok;
    if (sig.aborted) say('Descarga cancelada. Lo que ya llegó sigue disponible.');
    else if (!ok && bad === todo.length && todo.every((l) => (S.status[l.id] || '').includes('Sin conexión'))) say('<b>No hay conexión con los servicios oficiales desde esta página.</b> Si la abriste dentro de una vista previa incrustada, ábrela desde GitHub Pages o en tu computador (doble clic en index.html). Si no, revisa tu conexión y reintenta.');
    else say(`Listo: ${ok} capa(s) descargada(s)${bad ? `, ${bad} con error (usa ↻ para reintentar)` : ''}. Descárgalas una por una o todo en ZIP.`);
    if (ok) markStep(2);
  }
  async function retryLayer(id) { const l = LAYERS.find((x) => x.id === id); if (!S.boundary) return run(); S.running = true; await doLayer(l, new AbortController().signal); S.running = false; renderLayers(); $('zipBtn').disabled = !S.res.size; }
  $('runBtn').onclick = run;
  $('stopBtn').onclick = () => S.ctrl && S.ctrl.abort();

  $('zipBtn').onclick = () => {
    if (!S.res.size) return;
    const files = [...S.res.entries()].map(([id, r]) => ({ name: fileName(LAYERS.find((x) => x.id === id)), data: r.bytes }));
    const lines = [`GeoIA Colombia · TerraDrop`, `Territorio: ${title(S.mun.n)} (${S.mun.c}), ${title(S.mun.dn)}${S.ver ? ' · vereda ' + title(S.ver.nom) + ' (' + S.ver.cod + ')' : ''}`, `Fecha: ${new Date().toLocaleString('es-CO')}`, '', 'Capas incluidas:', ...[...S.res.entries()].map(([id, r]) => { const l = LAYERS.find((x) => x.id === id); return `- ${fileName(l)} · ${l.name} · ${r.count} elementos · ${l.small}`; }), '', 'Sistema de referencia: EPSG:4326 (WGS84).', 'Los elementos intersectan el límite elegido; no están recortados. En QGIS: Vector > Geoprocesamiento > Cortar.', 'Revisa la vigencia y las limitaciones de cada fuente en fuentes.html.'];
    files.push({ name: 'LEEME.txt', data: enc.encode(lines.join('\n')) });
    if (S.assign && S.assign.code === S.mun.c) files.push({ name: `asignacion_${S.mun.c}.geojson`, data: enc.encode(JSON.stringify(assignFeature())) });
    GEOQ.saveBlob(GEOQ.zip(files), `terradrop_${S.mun.c}_${slug(S.mun.n)}.zip`); markStep(2);
  };

  // ---------- mapa (canvas) ----------
  const cv = $('mapCanvas'), ctx = cv.getContext('2d');
  const view = { x: 0, y: 0, s: .5 }; let W = 800, H = 520, dpr = 1;
  const w = (lon, lat) => [(lon - P.minx) * P.k, (P.maxy - lat) * P.k];
  const base = Object.values(MAP.dep).filter((d) => d.p).map((d) => new Path2D(d.p));
  const muniPath = {}; const getMuniPath = (c) => muniPath[c] || (MAP.mun[c] ? (muniPath[c] = new Path2D(MAP.mun[c])) : null);
  function resize() { const r = cv.getBoundingClientRect(); dpr = window.devicePixelRatio || 1; W = r.width; H = r.height; cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr); draw(); }
  addEventListener('resize', resize);
  function fitBox(x0, y0, x1, y1, pad = 1.25) { const bw = Math.max(x1 - x0, 1), bh = Math.max(y1 - y0, 1); view.s = Math.min(W / (bw * pad), H / (bh * pad)); view.x = (x0 + x1) / 2 - W / (2 * view.s); view.y = (y0 + y1) / 2 - H / (2 * view.s); draw(); }
  function fitGeom(g) { const b = GEOQ.bboxOf(g); const a = w(b[0], b[3]), c = w(b[2], b[1]); fitBox(a[0], a[1], c[0], c[1]); }
  function fitSel() { if (!S.mun) return fitAll(); const b = S.mun.bb; const a = w(b[0], b[3]), c = w(b[2], b[1]); fitBox(a[0], a[1], c[0], c[1], 1.6); }
  function fitAll() { fitBox(0, 0, MAP.w, MAP.h, 1.08); }

  function buildItems(l, fc) {
    const items = []; const mk = () => new Path2D();
    const add = (p, geom) => {
      const ring = (r, close) => { r.forEach((c, i) => { const [x, y] = w(c[0], c[1]); i ? p.lineTo(x, y) : p.moveTo(x, y); }); if (close) p.closePath(); };
      const t = geom && geom.type, c = geom && geom.coordinates;
      if (t === 'Polygon') c.forEach((r) => ring(r, true)); else if (t === 'MultiPolygon') c.forEach((pl) => pl.forEach((r) => ring(r, true)));
      else if (t === 'LineString') ring(c); else if (t === 'MultiLineString') c.forEach((r) => ring(r));
    };
    if (l.id === 'clc2024') {
      const g = {}; fc.features.forEach((f) => { const k = String((f.properties && (f.properties.codigo || f.properties.nivel_1)) || '0').charAt(0); (g[k] || (g[k] = mk())); add(g[k], f.geometry); });
      Object.entries(g).forEach(([k, p]) => items.push({ p, fill: GEOQ.CLC_COL[k] || l.color, alpha: .75, stroke: null }));
    } else { const p = mk(); fc.features.forEach((f) => add(p, f.geometry)); items.push({ p, fill: l.kind === 'poly' ? l.color : null, alpha: l.id === 'veredas' ? .12 : l.id === 'runap' ? .35 : .15, stroke: l.color, lw: l.id === 'municipio' ? 2.4 : l.kind === 'line' ? 1.3 : 1 }); }
    return items;
  }
  const ORDER = ['clc2024', 'runap', 'veredas', 'drenajes', 'rios_principales', 'vias_tiempo_seco', 'vias_sin_pavimentar', 'vias_pavimentadas', 'municipio'];
  function draw() {
    ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, cv.width, cv.height);
    ctx.setTransform(dpr * view.s, 0, 0, dpr * view.s, -dpr * view.s * view.x, -dpr * view.s * view.y);
    const px = 1 / view.s; ctx.lineJoin = 'round'; ctx.lineCap = 'round';
    ctx.globalAlpha = S.res.size ? .45 : 1; ctx.fillStyle = '#e8e2d2'; ctx.strokeStyle = '#fff'; ctx.lineWidth = 1.4 * px;
    base.forEach((p) => { ctx.fill(p); ctx.stroke(p); });
    ctx.globalAlpha = 1;
    if (S.mun) {
      const mp = getMuniPath(S.mun.c);
      const shape = S.live && S.live.code === S.mun.c ? S.live.p : mp;
      if (shape && !S.boundary) { ctx.fillStyle = 'rgba(255,201,60,.9)'; ctx.strokeStyle = '#0d0d12'; ctx.lineWidth = 1.6 * px; ctx.fill(shape, 'evenodd'); ctx.stroke(shape); }
      if (view.s < 3) { const [x, y] = w(S.mun.lon, S.mun.lat); ctx.fillStyle = '#ff4d4d'; ctx.strokeStyle = '#0d0d12'; ctx.lineWidth = 2 * px; ctx.beginPath(); ctx.arc(x, y, 7 * px, 0, 7); ctx.fill(); ctx.stroke(); }
    }
    ORDER.forEach((id) => {
      const r = S.res.get(id); if (!r) return;
      r.items.forEach((it) => {
        if (it.fill) { ctx.globalAlpha = it.alpha; ctx.fillStyle = it.fill; ctx.fill(it.p); ctx.globalAlpha = 1; }
        if (it.stroke) { ctx.strokeStyle = it.stroke; ctx.lineWidth = (it.lw || 1) * px; ctx.stroke(it.p); }
      });
    });
  }
  function renderLegend() {
    const items = LAYERS.filter((l) => S.res.has(l.id)).map((l) => `<span><i style="background:${l.color}"></i>${esc(l.name)}</span>`);
    $('legend').innerHTML = items.length ? items.join('') : '<span><i style="background:#ffc93c"></i>Territorio elegido</span><span><i style="background:#ff4d4d"></i>Ubicación</span>';
  }
  let drag = null;
  cv.addEventListener('pointerdown', (e) => { drag = { x: e.clientX, y: e.clientY }; cv.setPointerCapture(e.pointerId); cv.style.cursor = 'grabbing'; });
  cv.addEventListener('pointermove', (e) => { if (!drag) return; view.x -= (e.clientX - drag.x) / view.s; view.y -= (e.clientY - drag.y) / view.s; drag = { x: e.clientX, y: e.clientY }; draw(); });
  cv.addEventListener('pointerup', () => { drag = null; cv.style.cursor = 'grab'; });
  function zoomAt(f, cx = W / 2, cy = H / 2) { const wx = view.x + cx / view.s, wy = view.y + cy / view.s; view.s = Math.max(.15, Math.min(400, view.s * f)); view.x = wx - cx / view.s; view.y = wy - cy / view.s; draw(); }
  cv.addEventListener('wheel', (e) => { e.preventDefault(); const r = cv.getBoundingClientRect(); zoomAt(e.deltaY < 0 ? 1.25 : .8, e.clientX - r.left, e.clientY - r.top); }, { passive: false });
  $('zin').onclick = () => zoomAt(1.5); $('zout').onclick = () => zoomAt(1 / 1.5); $('zfit').onclick = () => (S.boundary && S.boundary.geom ? fitGeom(S.boundary.geom) : S.mun ? fitSel() : fitAll());

  // ---------- asistente ----------
  const say = (h) => ($('say').innerHTML = h);
  function interpret(text) {
    const t = ' ' + norm(text) + ' '; const want = new Set(); const has = (re) => re.test(t);
    if (has(/ (todo|todas|completo|completa) /)) LAYERS.forEach((l) => want.add(l.id));
    if (has(/ (municipio|limite|limites|poligono) /)) want.add('municipio');
    if (has(/ vereda/)) want.add('veredas');
    if (has(/ (area|areas) protegid| runap | parque| reserva| protegid/)) want.add('runap');
    if (has(/ via | vias | carretera| camino| carreteable| transitable/)) ['vias_pavimentadas', 'vias_sin_pavimentar', 'vias_tiempo_seco'].forEach((x) => want.add(x));
    if (has(/ rio | rios | drenaje| hidro| agua | aguas | quebrada| cuenca/)) ['drenajes', 'rios_principales'].forEach((x) => want.add(x));
    if (has(/ cobertura| clc | corine| bosque| uso del suelo/)) want.add('clc2024');
    const random = has(/ azar | aleatori| sorte| cualquier /);
    const apOnly = has(/ protegid| runap /);
    // lugar
    const depMentioned = DEPS.filter((x) => t.includes(' ' + norm(x.dn.split(',')[0]) + ' '));
    let cands = MUN.filter((m) => { const a = norm(m.n), b = norm(m.n.split(',')[0]); return t.includes(' ' + a + ' ') || t.includes(' ' + b + ' '); });
    let mun = null, note = '';
    if (cands.length) {
      const L = Math.max(...cands.map((m) => norm(m.n.split(',')[0]).length)); cands = cands.filter((m) => norm(m.n.split(',')[0]).length === L);
      const inDep = cands.filter((m) => depMentioned.some((d) => d.d === m.d));
      if (inDep.length) cands = inDep;
      mun = cands[0]; if (cands.length > 1) note = ` Hay ${cands.length} municipios con ese nombre; tomé ${title(mun.dn)}. Cámbialo con los selectores si no es el tuyo.`;
    }
    return { want, mun, dep: depMentioned[0], random, apOnly, note };
  }
  async function ask(text) {
    const r = interpret(text);
    if (r.random && !r.mun) {
      const pool = MUN.filter((m) => (!r.apOnly || m.ap > 0) && (!r.dep || m.d === r.dep.d)); const m = pool[Math.floor(Math.random() * pool.length)];
      if (r.want.size) S.on = r.want; await selectMun(m.c);
      return say(`Sorteé <b>${esc(title(m.n))}</b> (${esc(title(m.dn))})${r.apOnly ? ', que tiene áreas protegidas' : ''}. Capas marcadas: ${S.on.size}. Pulsa <b>Descargar capas</b>.`);
    }
    if (!r.mun && !r.dep) return say('No reconocí el lugar. Prueba con el nombre del municipio, por ejemplo “veredas y ríos de Filandia, Quindío”.');
    if (r.want.size) S.on = r.want;
    if (r.mun) { await selectMun(r.mun.c); say(`Entendí <b>${esc(title(r.mun.n))}</b> (${esc(title(r.mun.dn))}) con <b>${S.on.size}</b> capa(s): ${LAYERS.filter((l) => S.on.has(l.id)).map((l) => l.name.toLowerCase()).join(', ')}.${esc(r.note)} Pulsa <b>Descargar capas</b>.`); }
    else { selDep.value = r.dep.d; fillMun(r.dep.d); clearSel(); say(`Activé el departamento <b>${esc(title(r.dep.dn))}</b>. Elige uno de sus ${MUN.filter((m) => m.d === r.dep.d).length} municipios.`); }
    renderLayers();
  }
  $('askForm').addEventListener('submit', (e) => { e.preventDefault(); const v = $('askInput').value.trim(); if (v) ask(v); });

  // ---------- Modo Aula ----------
  function setMode(m) {
    S.mode = m; const aula = m === 'aula';
    $('modeMun').setAttribute('aria-pressed', !aula); $('modeAula').setAttribute('aria-pressed', aula);
    $('aulaBox').hidden = !aula; $('routeBox').hidden = !aula; $('assignCard').hidden = !(aula && S.assign);
    $('pickTitle').textContent = aula ? 'Elige tú, o usa tu sorteo' : 'Elige el territorio';
    if (aula) refreshRoute();
    const u = new URL(location.href); aula ? u.searchParams.set('modo', 'aula') : u.searchParams.delete('modo'); history.replaceState(null, '', u);
  }
  $('modeMun').onclick = () => setMode('municipio'); $('modeAula').onclick = () => setMode('aula');

  function pool() { return MUN.filter((m) => (!$('onlyAP').checked || m.ap > 0) && (!$('drawScope').value || m.d === $('drawScope').value)).sort((a, b) => (a.c < b.c ? -1 : 1)); }
  async function drawMine(redraw) {
    const name = $('stuName').value.trim(); if (name.length < 2) { toast('Escribe tu nombre para sortear'); $('stuName').focus(); return; }
    const p = pool(); if (!p.length) return toast('No hay municipios con esos filtros');
    if (redraw) S.attempt++; else S.attempt = S.assign && S.assign.name === name ? S.assign.attempt || 0 : 0;
    const key = `${norm(name)}|${$('drawScope').value}|${$('onlyAP').checked}|${S.attempt}`;
    const m = p[hash(key) % p.length];
    S.assign = { name, code: m.c, attempt: S.attempt, when: new Date().toISOString() }; store.set('assign', S.assign); store.set('stu', name);
    $('redrawBtn').disabled = false; await selectMun(m.c); showAssign(); markStep(1);
    say(`<b>${esc(name)}</b>, tu municipio es <b>${esc(title(m.n))}</b> (${esc(title(m.dn))}). Descarga sus capas y sigue la ruta de aprendizaje.`);
  }
  $('drawBtn').onclick = () => drawMine(false); $('redrawBtn').onclick = () => drawMine(true);
  function pathBox(d) { const n = d.match(/-?\d+(?:\.\d+)?/g).map(Number); let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9; for (let i = 0; i < n.length; i += 2) { x0 = Math.min(x0, n[i]); x1 = Math.max(x1, n[i]); y0 = Math.min(y0, n[i + 1]); y1 = Math.max(y1, n[i + 1]); } return [x0, y0, x1, y1]; }
  function showAssign() {
    if (!S.assign) return; const m = byCode[S.assign.code]; $('assignCard').hidden = S.mode !== 'aula';
    $('aName').textContent = title(m.n);
    const d = MAP.mun[m.c];
    if (d) { const [x0, y0, x1, y1] = pathBox(d), pw = Math.max(x1 - x0, 1), ph = Math.max(y1 - y0, 1), pad = Math.max(pw, ph) * .08; $('assignSvg').setAttribute('viewBox', `${x0 - pad} ${y0 - pad} ${pw + 2 * pad} ${ph + 2 * pad}`); $('assignSvg').innerHTML = `<path d="${d}" fill="#ffc93c" stroke="#0d0d12" stroke-width="${Math.max(pw, ph) / 60}" stroke-linejoin="round"/>`; }
    else $('assignSvg').innerHTML = '<circle cx="50" cy="60" r="18" fill="#ff4d4d"/>';
    const names = m.na ? m.na.split(' | ') : [];
    $('aDl').innerHTML = [['Estudiante', S.assign.name], ['Código DANE', m.c], ['Departamento', title(m.dn)], ['Área', fmt(Math.round(m.a * 10) / 10) + ' km²'], ['Áreas protegidas', m.ap ? `${m.ap}: ${names.slice(0, 3).join(', ')}${names.length > 3 ? '…' : ''}` : 'ninguna en el índice'], ['Ríos principales', m.nr || '—']].map(([a, b]) => `<dt>${a}</dt><dd>${esc(b)}</dd>`).join('');
  }
  function assignFeature() {
    const m = byCode[S.assign.code];
    return { type: 'FeatureCollection', name: 'asignacion_' + m.c, features: [{ type: 'Feature', geometry: { type: 'Point', coordinates: [m.lon, m.lat] }, properties: { estudiante: S.assign.name, asignado: S.assign.when, cod_dane: m.c, municipio: title(m.n), departamento: title(m.dn), area_km2: m.a, areas_protegidas: m.ap, nombres_areas: m.na, rios_principales: m.nr, humedales_mads_v3: m.hm } }] };
  }
  $('aDown').onclick = () => { const m = byCode[S.assign.code]; GEOQ.saveBlob(new Blob([JSON.stringify(assignFeature(), null, 1)], { type: 'application/geo+json' }), `asignacion_${m.c}.geojson`); };

  // ruta de aprendizaje
  const STEPS = [
    { t: 'Recibe tu municipio', d: 'Escribe tu nombre y pulsa “Sortear” (o elige uno tú).' },
    { t: 'Descarga tus capas', d: 'Pulsa “Descargar capas” y guarda el ZIP.' },
    { t: 'Ábrelas en QGIS o Colab', d: 'Arrastra los .geojson al lienzo. Toca aquí cuando lo logres.', manual: true },
    { t: 'Entiende el geovisor', d: 'Lee por qué el visor es el núcleo de la información.', href: 'aula.html' },
    { t: 'Practica clic a clic', d: 'Recorre Colombia en Mapas con el tutorial.', href: 'colombia-en-mapas.html' },
  ];
  const rk = () => 'route:' + (S.assign ? S.assign.code : S.mun ? S.mun.c : '-');
  function markStep(i) { const r = store.get(rk(), []); if (!r.includes(i)) { r.push(i); store.set(rk(), r); } refreshRoute(); }
  function refreshRoute() {
    const done = store.get(rk(), []);
    $('route').innerHTML = STEPS.map((s, i) => `<li class="${done.includes(i + 1) ? 'done' : ''}" ${s.manual ? `data-manual="${i + 1}" style="cursor:pointer"` : ''}><div><b>${s.href ? `<a href="${s.href}" data-step="${i + 1}">${s.t} →</a>` : s.t}</b><br><span style="color:var(--muted);font-size:.9rem">${s.d}</span></div></li>`).join('');
  }
  $('route').addEventListener('click', (e) => {
    const a = e.target.closest('[data-step]'); if (a) { markStep(+a.dataset.step); return; }
    const m = e.target.closest('[data-manual]'); if (m) markStep(+m.dataset.manual);
  });

  // ---------- arranque ----------
  new ResizeObserver(resize).observe(cv); resize(); fitAll(); renderLayers();
  const q = new URLSearchParams(location.search);
  if (store.get('stu', '')) $('stuName').value = store.get('stu', '');
  if (q.get('modo') === 'aula') setMode('aula');
  if (S.assign && byCode[S.assign.code] && S.mode === 'aula') { $('redrawBtn').disabled = false; await selectMun(S.assign.code); showAssign(); }
  if (q.get('mun') && byCode[q.get('mun')]) await selectMun(q.get('mun'), { ver: q.get('ver') || undefined });
  if (q.get('q')) { $('askInput').value = q.get('q'); await ask(q.get('q')); }
})();
