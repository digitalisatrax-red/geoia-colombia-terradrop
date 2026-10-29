"""Crea data/*.js (copias de data/*.json para abrir el sitio con doble clic, sin servidor).
Ejecutar después de cambiar cualquier JSON de data/:  python3 scripts/make_data_js.py"""
import json, os
d = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
for n in ('municipios', 'mapa_colombia', 'fuentes_base_nacional'):
    j = json.load(open(os.path.join(d, n + '.json'), encoding='utf-8'))
    s = 'window.__GEO_DATA=window.__GEO_DATA||{};window.__GEO_DATA["data/%s.json"]=%s;' % (n, json.dumps(j, ensure_ascii=False, separators=(',', ':')))
    open(os.path.join(d, n + '.js'), 'w', encoding='utf-8').write(s); print(n + '.js', len(s))
