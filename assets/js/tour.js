/* Tutorial interactivo: réplica didáctica del visor Colombia en Mapas (IGAC).
   Los pasos se basan en la guía creada en Lovable ("Colombia en Mapas Fácil"). */
(async function () {
  const $ = (id) => document.getElementById(id);
  const IC = {
    search: '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    filter: '<polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>',
    pin: '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    layers: '<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>',
    mountain: '<path d="m8 3 4 8 5-5 5 15H2L8 3z"/>',
    sprout: '<path d="M7 20h10"/><path d="M10 20c5.5-2.5.8-6.4 3-10"/><path d="M9.5 9.4c1.1.8 1.8 2.2 2.3 3.7-2 .4-3.5.4-4.8-.3-1.2-.6-2.3-1.9-3-4.2 2.8-.5 4.4 0 5.5.8z"/><path d="M14.1 6a7 7 0 0 0-1.1 4c1.9-.1 3.3-.6 4.3-1.4 1-1 1.6-2.3 1.7-4.6-2.7.1-4 1-4.9 2z"/>',
    landmark: '<path d="M3 22h18"/><path d="M6 18v-7"/><path d="M10 18v-7"/><path d="M14 18v-7"/><path d="M18 18v-7"/><path d="M12 2 20 7H4z"/>',
    list: '<path d="M8 6h13"/><path d="M8 12h13"/><path d="M8 18h13"/><path d="M3 6h.01"/><path d="M3 12h.01"/><path d="M3 18h.01"/>',
    upload: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>',
    ruler: '<path d="M21.3 15.3a2.4 2.4 0 0 1 0 3.4l-2.6 2.6a2.4 2.4 0 0 1-3.4 0L2.7 8.7a2.4 2.4 0 0 1 0-3.4l2.6-2.6a2.4 2.4 0 0 1 3.4 0Z"/><path d="m14.5 12.5 2-2"/><path d="m11.5 9.5 2-2"/><path d="m8.5 6.5 2-2"/><path d="m17.5 15.5 2-2"/>',
    shapes: '<path d="M8.3 10a.7.7 0 0 1-.6-1.1L11.4 3a.7.7 0 0 1 1.2 0l3.7 5.9a.7.7 0 0 1-.6 1.1Z"/><rect x="3" y="14" width="7" height="7" rx="1"/><circle cx="17.5" cy="17.5" r="3.5"/>',
    printer: '<polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/>',
    share: '<circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.6" y1="13.5" x2="15.4" y2="17.5"/><line x1="15.4" y1="6.5" x2="8.6" y2="10.5"/>',
    info: '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>',
    globe: '<circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
    user: '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    home: '<path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>',
    plus: '<path d="M5 12h14"/><path d="M12 5v14"/>',
    minus: '<path d="M5 12h14"/>',
    cross: '<circle cx="12" cy="12" r="10"/><line x1="22" y1="12" x2="18" y2="12"/><line x1="6" y1="12" x2="2" y2="12"/><line x1="12" y1="6" x2="12" y2="2"/><line x1="12" y1="22" x2="12" y2="18"/>',
    chev: '<polyline points="9 18 15 12 9 6"/>',
  };
  const svg = (k) => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${IC[k]}</svg>`;

  const STEPS = [
    { id: 'bienvenida', ic: 'info', short: '', title: 'Bienvenida al visor', what: 'Colombia en Mapas es el geovisor del IGAC que reúne cartografía, imágenes satelitales, catastro, suelos y más en un solo lugar.', how: ['Observa los tres grupos de controles: la barra superior, los botones del mapa y el panel lateral.', 'Pulsa “Siguiente” para recorrerlos en orden, o haz clic en cualquier botón del visor para ir directo a su explicación.'], kind: 'welcome' },
    { id: 'explorar', ic: 'search', short: 'Explorar', title: 'Explorar', what: 'Abre el catálogo de información geográfica: cartografía, imágenes satelitales, geodesia, catastro y más.', how: ['Haz clic en la lupa de la barra superior.', 'Escribe un tema o lugar en el buscador (ej. “Ríos” o “Medellín”).', 'Selecciona un resultado para verlo en el mapa.'] },
    { id: 'filtros', ic: 'filter', short: 'Filtros', title: 'Filtros', what: 'Refina los resultados por año, escala, tipo de imagen, sensor, resolución o licencia.', how: ['Haz clic en el embudo.', 'Elige los criterios (Año, Escala, Licencia...).', 'Los resultados del catálogo se actualizan solos.'] },
    { id: 'coordenadas', ic: 'pin', short: 'Coordenadas', title: 'Coordenadas y alturas', what: 'Consulta la latitud, longitud y altura sobre el nivel del mar de cualquier punto.', how: ['Activa la herramienta.', 'Haz clic sobre un punto del mapa.', 'Lee las coordenadas y la altura en el panel; también puedes escribir coordenadas para ubicarlas.'] },
    { id: 'suelo', ic: 'layers', short: 'Suelo', title: 'Uso del suelo', what: 'Muestra para qué se usa la tierra en un lugar (agrícola, forestal, urbano...).', how: ['Activa “Uso del suelo”.', 'Haz clic en una zona del mapa.', 'Revisa la vocación y el uso recomendado.'] },
    { id: 'agro', ic: 'sprout', short: 'Agrología', title: 'Clases agrológicas', what: 'Indica la capacidad del suelo para cultivos según la clasificación del IGAC (clases I a VIII).', how: ['Activa la herramienta.', 'Haz clic en el lugar de interés.', 'Consulta la clase y sus limitaciones.'] },
    { id: 'catastral', ic: 'landmark', short: 'Catastral', title: 'Catastral', what: 'Busca predios por número predial, matrícula o ubicación y consulta su información catastral.', how: ['Abre “Catastral”.', 'Escribe el número predial (30 dígitos) o haz clic en el predio.', 'Revisa área de terreno, construcción y destino.'] },
    { id: 'leyenda', ic: 'list', short: 'Leyenda', title: 'Leyenda', what: 'Explica los colores y símbolos de las capas que tienes encendidas.', how: ['Haz clic en “Leyenda”.', 'Identifica qué significa cada color o símbolo.'] },
    { id: 'capas', ic: 'layers', short: 'Capas', title: 'Capas activas', what: 'Lista las capas visibles: puedes encenderlas, apagarlas, cambiar su orden y transparencia.', how: ['Abre “Capas activas”.', 'Usa el interruptor para mostrar u ocultar.', 'Arrastra para reordenar o ajusta la transparencia.'] },
    { id: 'importar', ic: 'upload', short: 'Importar', title: 'Importar datos', what: 'Carga tus propios archivos (Shapefile .zip, KML, GeoJSON, CSV) o servicios WMS.', how: ['Haz clic en “Importar datos”.', 'Selecciona el archivo o pega la URL del servicio.', 'Tu capa aparecerá en “Capas activas”.'], tip: 'Los GeoJSON que descargas con TerraDrop se pueden cargar aquí.' },
    { id: 'medir', ic: 'ruler', short: 'Medir', title: 'Dibujar y medir', what: 'Dibuja puntos, líneas o polígonos y mide distancias y áreas.', how: ['Elige la figura (línea o polígono).', 'Haz clic en el mapa para cada vértice; doble clic para terminar.', 'Lee la distancia o el área resultante.'] },
    { id: 'operaciones', ic: 'shapes', short: 'Operaciones', title: 'Operaciones espaciales', what: 'Análisis como áreas de influencia (buffer), intersección o selección por ubicación.', how: ['Selecciona la operación.', 'Escoge la capa o figura de entrada y el parámetro (ej. 500 m).', 'Ejecuta y revisa el resultado en el mapa.'] },
    { id: 'imprimir', ic: 'printer', short: 'Imprimir', title: 'Imprimir', what: 'Genera un mapa en PDF o imagen con título, escala y leyenda.', how: ['Encuadra la zona que quieres.', 'Haz clic en “Imprimir”, escribe el título y elige tamaño.', 'Descarga el archivo.'] },
    { id: 'compartir', ic: 'share', short: 'Compartir', title: 'Compartir', what: 'Crea un enlace con la vista actual del mapa para enviarlo a otras personas.', how: ['Haz clic en “Compartir”.', 'Copia el enlace o compártelo en redes.'] },
    { id: 'info', ic: 'info', short: 'Info', title: 'Información', what: 'Acceso al tutorial oficial, exploración rápida y “Acerca de”.', how: ['Haz clic en la “i”.', 'Elige Tutorial y FAQ para ayuda oficial.'] },
    { id: 'idioma', ic: 'globe', short: 'ES/EN', title: 'Cambiar idioma', what: 'Cambia la interfaz entre español (ES) e inglés (EN).', how: ['Haz clic en el selector ES ⇆ EN.'] },
    { id: 'sesion', ic: 'user', short: 'Sesión', title: 'Iniciar sesión', what: 'Entra con tu cuenta para guardar mapas y descargar ciertos productos.', how: ['Haz clic en el ícono de usuario.', 'Ingresa o crea tu cuenta.'] },
    { id: 'inicio', ic: 'home', short: 'Inicio', title: 'Inicio', what: 'Vuelve a la página principal del portal.', how: ['Haz clic en la casa de la barra superior.'] },
    { id: 'panel', ic: 'chev', title: 'Panel de información general', what: 'Despliega datos de Colombia: capital, área, predios, estaciones CORS, planchas históricas.', how: ['Haz clic en la flecha del borde izquierdo.', 'Pulsa los números en azul para ver esos datos en el mapa.'], kind: 'map' },
    { id: 'extension', ic: 'home', title: 'Vista completa', what: 'Regresa el mapa a la vista de todo el país.', how: ['Haz clic en la casa de la esquina inferior derecha.'], kind: 'map' },
    { id: 'ubicacion', ic: 'cross', title: 'Mi ubicación', what: 'Centra el mapa en donde te encuentras.', how: ['Haz clic y acepta el permiso de ubicación del navegador.'], kind: 'map' },
    { id: 'zoomin', ic: 'plus', title: 'Acercar', what: 'Aumenta el zoom. También con la rueda del ratón o doble clic.', how: ['Pulsa “+” o gira la rueda hacia adelante.'], kind: 'map' },
    { id: 'zoomout', ic: 'minus', title: 'Alejar', what: 'Reduce el zoom para ver más territorio.', how: ['Pulsa “−” o gira la rueda hacia atrás.'], kind: 'map' },
    { id: 'coords', ic: 'pin', title: 'Barra de coordenadas y escala', what: 'Muestra las coordenadas del puntero (EPSG:9377, origen nacional) y la escala gráfica.', how: ['Mueve el ratón sobre el mapa y observa cómo cambian los valores.'], kind: 'map' },
  ];
  const idx = Object.fromEntries(STEPS.map((s, i) => [s.id, i]));
  let cur = 0; const seen = new Set([0]);

  // fondo ilustrado
  let MAP = null; try { MAP = await GEO.json('data/mapa_colombia.json'); } catch (e) { /* sin fondo */ }
  const deps = MAP ? Object.values(MAP.dep).filter((d) => d.p) : [];
  $('bg').innerHTML = `<defs><linearGradient id="sea" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0a2a3e"/><stop offset="1" stop-color="#0d4a5f"/></linearGradient><radialGradient id="land" cx=".4" cy=".35" r=".9"><stop offset="0" stop-color="#4f8f5f"/><stop offset=".6" stop-color="#2f6c4c"/><stop offset="1" stop-color="#1d4a3a"/></radialGradient></defs><rect width="1000" height="625" fill="url(#sea)"/>${MAP ? `<g transform="translate(330,24) scale(.33)">${deps.map((d) => `<path d="${d.p}" fill="url(#land)" stroke="#0b2a3a" stroke-width="3" stroke-linejoin="round"/>`).join('')}</g>` : ''}<g stroke="#ffffff" stroke-opacity=".06">${Array.from({ length: 10 }, (_, i) => `<path d="M0 ${62 * i}H1000"/>`).join('')}${Array.from({ length: 16 }, (_, i) => `<path d="M${62 * i} 0V625"/>`).join('')}</g>`;

  // botones
  $('vbar').innerHTML = STEPS.filter((s) => !s.kind).map((s) => `<button class="vbtn" data-id="${s.id}" aria-label="${s.title}">${svg(s.ic)}<span>${s.short}</span></button>`).join('');
  $('vpanel').innerHTML = svg('chev').replace('<svg', '<svg width="20" height="20"');
  $('mctls').innerHTML = ['extension', 'ubicacion', 'zoomin', 'zoomout'].map((id) => `<button class="mctl" data-id="${id}" aria-label="${STEPS[idx[id]].title}">${svg(STEPS[idx[id]].ic)}</button>`).join('');
  $('jump').innerHTML = STEPS.map((s, i) => `<option value="${i}">${i + 1}. ${s.title}</option>`).join('');

  function go(i) {
    cur = Math.max(0, Math.min(STEPS.length - 1, i)); seen.add(cur); const s = STEPS[cur];
    document.querySelectorAll('[data-id]').forEach((el) => el.classList.toggle('active', el.dataset.id === s.id));
    $('tn').textContent = `Paso ${cur + 1} de ${STEPS.length} · ${s.kind === 'map' ? 'Controles del mapa' : s.kind === 'welcome' ? 'Introducción' : 'Barra superior'}`;
    $('tt').textContent = s.title; $('tw').textContent = s.what;
    $('th').innerHTML = s.how.map((h) => `<li>${h}</li>`).join('') + (s.tip ? `<li style="list-style:none;margin-left:-22px;margin-top:10px"><span class="stat ok" style="white-space:normal;display:block;padding:8px 12px">💡 ${s.tip}</span></li>` : '');
    $('tbar').style.width = Math.round(((cur + 1) / STEPS.length) * 100) + '%';
    $('prev').disabled = cur === 0; $('next').disabled = cur === STEPS.length - 1; $('jump').value = cur;
    const last = cur === STEPS.length - 1; $('finish').hidden = !last;
    if (last) { const a = GEO.store.get('assign', null); if (a) { const k = 'route:' + a.code, r = GEO.store.get(k, []); if (!r.includes(5)) { r.push(5); GEO.store.set(k, r); } } }
  }
  $('visor').addEventListener('click', (e) => { const t = e.target.closest('[data-id]'); if (t) go(idx[t.dataset.id]); });
  $('prev').onclick = () => go(cur - 1); $('next').onclick = () => go(cur + 1);
  $('jump').onchange = (e) => go(+e.target.value);
  addEventListener('keydown', (e) => { if (/INPUT|SELECT|TEXTAREA/.test((e.target.tagName || ''))) return; if (e.key === 'ArrowRight') go(cur + 1); if (e.key === 'ArrowLeft') go(cur - 1); });
  $('visor').addEventListener('pointermove', (e) => { const r = $('visor').getBoundingClientRect(), x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height; $('cxy').textContent = `${(12.5 - y * 17).toFixed(4)}° ${12.5 - y * 17 >= 0 ? 'N' : 'S'} · ${(79 - x * 12.5).toFixed(4)}° W`; });
  go(0);
})();
