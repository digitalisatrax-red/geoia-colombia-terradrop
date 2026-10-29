/* GeoIA Colombia · motor de capas: catálogo de servicios, consulta paginada ArcGIS REST, ZIP sin dependencias.
   Servicios verificados el 2026-10-28 desde un navegador (responden con CORS abierto). */
(function () {
  const IDEAM = 'https://visualizador.ideam.gov.co/gisserver/rest/services';
  const INTERES = 'https://services2.arcgis.com/RVvWzU3lgJISqdke/arcgis/rest/services/Interes_Colombia/FeatureServer';

  // spatial:true -> se filtra con el polígono del territorio; where -> filtro por atributo
  const LAYERS = [
    { id: 'municipio', name: 'Límite municipal', small: 'DANE · Marco Geoestadístico (vía IDEAM)', color: '#0d0d12', kind: 'poly', page: 1000,
      url: IDEAM + '/Entidades_Territoriales/FeatureServer/2/query', where: (s) => `num_dane='${s.mun.c}'` },
    { id: 'veredas', name: 'Veredas DANE 2024', small: 'DANE · Veredas (vía IDEAM)', color: '#ff9f1c', kind: 'poly', page: 1000,
      url: IDEAM + '/Entidades_Territoriales/FeatureServer/5/query', where: (s) => (s.ver ? `cod_ver='${s.ver.cod}'` : `cod_mpio='${s.mun.c}'`) },
    { id: 'runap', name: 'Áreas protegidas (RUNAP)', small: 'MinAmbiente · OTL Área protegida', color: '#27c98f', kind: 'poly', page: 500, spatial: true,
      url: 'https://geo.minambiente.gov.co/server/rest/services/OTL/OTL_Area_Protegida/FeatureServer/0/query' },
    { id: 'vias_pavimentadas', name: 'Vías pavimentadas', small: 'IGAC · Interés Colombia', color: '#ff4d4d', kind: 'line', page: 1000, spatial: true, url: INTERES + '/16/query' },
    { id: 'vias_sin_pavimentar', name: 'Vías sin pavimentar', small: 'IGAC · Interés Colombia', color: '#ff7ab0', kind: 'line', page: 1000, spatial: true, url: INTERES + '/15/query' },
    { id: 'vias_tiempo_seco', name: 'Vías transitables en tiempo seco', small: 'IGAC · Interés Colombia', color: '#b9763f', kind: 'line', page: 1000, spatial: true, url: INTERES + '/14/query' },
    { id: 'drenajes', name: 'Drenajes (hidrografía)', small: 'Capa HIDROGRAFIA · ArcGIS Online', color: '#2f9bff', kind: 'line', page: 1000, spatial: true,
      url: 'https://services.arcgis.com/vC1CdlKWEAtuT38d/ArcGIS/rest/services/HIDROGRAFIA/FeatureServer/0/query' },
    { id: 'rios_principales', name: 'Ríos principales', small: 'Interés Colombia · no es la red completa', color: '#0b4fcf', kind: 'line', page: 1000, spatial: true, url: INTERES + '/8/query' },
    { id: 'clc2024', name: 'Coberturas CLC 2024', small: 'IDEAM · Corine Land Cover 1:100.000', color: '#8b6cf0', kind: 'poly', page: 1000, spatial: true,
      url: IDEAM + '/Estado_Cobertura_Tierra/MapServer/10/query' },
  ];

  // colores de CLC por nivel 1 (primer dígito del código)
  const CLC_COL = { 1: '#d95a5a', 2: '#e8c34b', 3: '#3fa56b', 4: '#7fc4b8', 5: '#4d8fe8' };

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  async function fetchRetry(url, opts, tries = 3, timeout = 60000) {
    let last;
    for (let i = 0; i < tries; i++) {
      const ac = new AbortController();
      const abortOuter = () => ac.abort();
      if (opts.signal) opts.signal.addEventListener('abort', abortOuter, { once: true });
      const to = setTimeout(() => ac.abort(), timeout);
      try {
        const r = await fetch(url, { ...opts, signal: ac.signal });
        clearTimeout(to);
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r;
      } catch (e) {
        clearTimeout(to); last = e;
        if (opts.signal && opts.signal.aborted) throw new Error('Cancelado');
        if (i < tries - 1) await sleep(900 * (i + 1));
      }
    }
    throw new Error(last && last.name === 'AbortError' ? 'El servicio tardó demasiado' : last && last.name === 'TypeError' ? 'Sin conexión con el servicio (red bloqueada o sin internet)' : (last && last.message) || 'Sin respuesta');
  }

  // Douglas-Peucker iterativo sobre un anillo [[x,y],...]
  function simplifyRing(ring, tol) {
    if (ring.length < 12) return ring;
    const keep = new Uint8Array(ring.length); keep[0] = keep[ring.length - 1] = 1;
    const st = [[0, ring.length - 1]];
    const t2 = tol * tol;
    while (st.length) {
      const [a, b] = st.pop(); let md = 0, mi = -1;
      const [ax, ay] = ring[a], [bx, by] = ring[b]; const dx = bx - ax, dy = by - ay, l2 = dx * dx + dy * dy;
      for (let i = a + 1; i < b; i++) {
        const [px, py] = ring[i]; let t = l2 ? ((px - ax) * dx + (py - ay) * dy) / l2 : 0; t = Math.max(0, Math.min(1, t));
        const ex = ax + t * dx - px, ey = ay + t * dy - py, d = ex * ex + ey * ey;
        if (d > md) { md = d; mi = i; }
      }
      if (md > t2 && mi > 0) { keep[mi] = 1; st.push([a, mi], [mi, b]); }
    }
    return ring.filter((_, i) => keep[i]);
  }

  function polygonsOf(geom) {
    if (!geom) return [];
    if (geom.type === 'Polygon') return [geom.coordinates];
    if (geom.type === 'MultiPolygon') return geom.coordinates;
    return [];
  }

  function bboxOf(geom) {
    let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
    const walk = (c) => { if (typeof c[0] === 'number') { if (c[0] < x0) x0 = c[0]; if (c[0] > x1) x1 = c[0]; if (c[1] < y0) y0 = c[1]; if (c[1] > y1) y1 = c[1]; } else c.forEach(walk); };
    walk(geom.coordinates || geom); return [x0, y0, x1, y1];
  }

  // geometría de filtro para ArcGIS: polígono simplificado (<= ~4000 vértices) o, si falla, envolvente
  function esriFilter(geom, mode) {
    const bb = bboxOf(geom);
    if (mode === 'envelope') return { type: 'esriGeometryEnvelope', esri: { xmin: bb[0], ymin: bb[1], xmax: bb[2], ymax: bb[3], spatialReference: { wkid: 4326 } } };
    let tol = 0.0003, rings;
    for (let k = 0; k < 6; k++) {
      rings = []; let n = 0;
      polygonsOf(geom).forEach((poly) => poly.forEach((r) => { const s = simplifyRing(r, tol); if (s.length >= 4) { rings.push(s); n += s.length; } }));
      if (n <= 4000) break; tol *= 2.2;
    }
    return { type: 'esriGeometryPolygon', esri: { rings, spatialReference: { wkid: 4326 } } };
  }

  async function query(layer, scope, onProgress, signal) {
    const where = layer.where ? layer.where(scope) : '1=1';
    const features = []; let offset = 0; let mode = 'polygon', note = '';
    for (;;) {
      const body = new URLSearchParams({ where, outFields: '*', outSR: '4326', returnGeometry: 'true', f: 'geojson', resultOffset: String(offset), resultRecordCount: String(layer.page) });
      if (layer.spatial && scope.geom) {
        const f = esriFilter(scope.geom, mode);
        body.set('geometry', JSON.stringify(f.esri)); body.set('geometryType', f.type); body.set('inSR', '4326'); body.set('spatialRel', 'esriSpatialRelIntersects');
      }
      let j;
      try {
        const r = await fetchRetry(layer.url, { method: 'POST', body, signal }, 3, 70000);
        j = await r.json();
        if (j.error) throw new Error(j.error.message || 'El servicio devolvió un error');
      } catch (e) {
        if (layer.spatial && mode === 'polygon' && offset === 0 && e.message !== 'Cancelado') { mode = 'envelope'; note = 'Se usó la envolvente del territorio porque el servicio no aceptó el polígono.'; continue; }
        throw e;
      }
      const got = j.features || []; features.push(...got); onProgress && onProgress(features.length);
      const more = j.exceededTransferLimit === true || (j.properties && j.properties.exceededTransferLimit === true);
      if (!got.length || (!more && got.length < layer.page)) break;
      offset += got.length; if (offset > 250000) break;
    }
    return { type: 'FeatureCollection', name: layer.id, features, metadata: { capa: layer.name, fuente: layer.small, servicio: layer.url, filtro: where, filtro_espacial: layer.spatial ? mode : 'no', consultado: new Date().toISOString(), nota: note || undefined } };
  }

  // Límite del territorio (vereda o municipio) como GeoJSON
  async function boundary(scope, signal) {
    const layer = scope.ver ? LAYERS[1] : LAYERS[0];
    const fc = await query(layer, scope, null, signal);
    const f = fc.features[0];
    return f ? { fc, geom: f.geometry } : { fc, geom: null };
  }

  // Límite del municipio para dibujarlo en el mapa: geometría real y liviana, pedida en vivo a la API
  async function limitPreview(code, signal, ver) {
    const L = ver ? LAYERS[1] : LAYERS[0];
    const body = new URLSearchParams({ where: ver ? `cod_ver='${ver}'` : `num_dane='${code}'`, outFields: ver ? 'cod_ver' : 'num_dane', outSR: '4326', returnGeometry: 'true', maxAllowableOffset: '0.0004', geometryPrecision: '5', f: 'geojson' });
    const r = await fetchRetry(L.url, { method: 'POST', body, signal }, 1, 20000);
    const j = await r.json(); const f = j.features && j.features[0];
    return f ? f.geometry : null;
  }

  // Busca veredas por nombre en todo el país (consulta en vivo, sin geometría)
  async function searchVeredas(text, signal) {
    const raw = String(text).trim().toUpperCase().replace(/'/g, "''").replace(/[%_]/g, '');
    if (raw.length < 3) return [];
    const plain = raw.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    const where = [...new Set([raw, plain])].map((t) => `UPPER(nom_ver) LIKE '%${t}%'`).join(' OR ');
    const p = new URLSearchParams({ where, outFields: 'cod_ver,nom_ver,cod_mpio', returnGeometry: 'false', orderByFields: 'nom_ver', resultRecordCount: '40', f: 'json' });
    const r = await fetchRetry(LAYERS[1].url, { method: 'POST', body: p, signal }, 2, 25000);
    const j = await r.json(); if (j.error) throw new Error(j.error.message || 'El servicio devolvió un error');
    return (j.features || []).map((f) => ({ cod: f.attributes.cod_ver, nom: f.attributes.nom_ver, mun: f.attributes.cod_mpio }));
  }

  async function listVeredas(code, signal) {
    const p = new URLSearchParams({ where: `cod_mpio='${code}'`, outFields: 'cod_ver,nom_ver', returnGeometry: 'false', orderByFields: 'nom_ver', f: 'json' });
    const r = await fetchRetry(LAYERS[1].url + '?' + p, { signal }, 2, 25000);
    const j = await r.json(); if (j.error) throw new Error(j.error.message);
    return (j.features || []).map((f) => ({ cod: f.attributes.cod_ver, nom: f.attributes.nom_ver }));
  }

  // ---- ZIP (almacenado, sin compresión) ----
  const CRC_T = (() => { const t = []; for (let n = 0; n < 256; n++) { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1; t[n] = c >>> 0; } return t; })();
  const crc32 = (u8) => { let c = 0xFFFFFFFF; for (let i = 0; i < u8.length; i++) c = CRC_T[(c ^ u8[i]) & 255] ^ (c >>> 8); return (c ^ 0xFFFFFFFF) >>> 0; };
  function zip(files) {
    const enc = new TextEncoder(), chunks = [], central = []; let offset = 0;
    const d = new Date(), time = (d.getHours() << 11) | (d.getMinutes() << 5) | (d.getSeconds() >> 1), date = ((d.getFullYear() - 1980) << 9) | ((d.getMonth() + 1) << 5) | d.getDate();
    for (const f of files) {
      const nb = enc.encode(f.name), data = f.data, crc = crc32(data), size = data.length;
      const lh = new DataView(new ArrayBuffer(30));
      lh.setUint32(0, 0x04034b50, true); lh.setUint16(4, 20, true); lh.setUint16(6, 0x0800, true); lh.setUint16(10, time, true); lh.setUint16(12, date, true);
      lh.setUint32(14, crc, true); lh.setUint32(18, size, true); lh.setUint32(22, size, true); lh.setUint16(26, nb.length, true);
      chunks.push(new Uint8Array(lh.buffer), nb, data);
      const ch = new DataView(new ArrayBuffer(46));
      ch.setUint32(0, 0x02014b50, true); ch.setUint16(4, 20, true); ch.setUint16(6, 20, true); ch.setUint16(8, 0x0800, true); ch.setUint16(12, time, true); ch.setUint16(14, date, true);
      ch.setUint32(16, crc, true); ch.setUint32(20, size, true); ch.setUint32(24, size, true); ch.setUint16(28, nb.length, true); ch.setUint32(42, offset, true);
      central.push(new Uint8Array(ch.buffer), nb); offset += 30 + nb.length + size;
    }
    const cd = central.reduce((a, b) => a + b.length, 0);
    const end = new DataView(new ArrayBuffer(22));
    end.setUint32(0, 0x06054b50, true); end.setUint16(8, files.length, true); end.setUint16(10, files.length, true); end.setUint32(12, cd, true); end.setUint32(16, offset, true);
    return new Blob([...chunks, ...central, new Uint8Array(end.buffer)], { type: 'application/zip' });
  }

  function saveBlob(blob, name) {
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = name;
    document.body.appendChild(a); a.click(); setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 4000);
  }

  window.LAYERS = LAYERS;
  window.GEOQ = { query, boundary, limitPreview, searchVeredas, listVeredas, zip, saveBlob, bboxOf, CLC_COL, simplifyRing, polygonsOf };
})();
