"""Genera data/mapa_colombia.json a partir de las partes GeoJSON del servicio IDEAM
(Entidades_Territoriales/FeatureServer/2). Simplificación topológica (los límites compartidos
no se separan) y trazos con 1 decimal en unidades de 0,01 grado.
Uso: python3 scripts/build_map.py CARPETA_PARTES [tolerancia_en_grados]"""
import glob, json, sys, os
import shapely
from shapely.geometry import shape, Polygon, MultiPolygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

src = sys.argv[1]; tol = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0008
here = os.path.dirname(os.path.abspath(__file__))
old = json.load(open(os.path.join(here, '..', 'data', 'mapa_colombia.json')))
P = old['proj']; K = P['k']; MINX, MAXY = P['minx'], P['maxy']
feats = []
for f in sorted(glob.glob(os.path.join(src, 'municipios_nacional_parte_*.geojson'))):
    feats += json.load(open(f))['features']
codes, geoms = [], []
for ft in feats:
    g = shape(ft['geometry']).buffer(0)
    code = ft['properties']['num_dane']
    if g.is_empty or g.centroid.x < MINX: continue          # fuera del mapa continental
    codes.append(code); geoms.append(g)
print('municipios', len(codes))
simp = shapely.coverage_simplify(geoms, tol) if hasattr(shapely, 'coverage_simplify') else [g.simplify(tol, preserve_topology=True) for g in geoms]

def ring_path(coords):
    pts = [f'{(x-MINX)*K:.1f},{(MAXY-y)*K:.1f}' for x, y in coords[:-1]]
    return 'M' + ' '.join(pts) + 'Z'
def path_of(g, min_hole=0.0):
    polys = [g] if isinstance(g, Polygon) else [p for p in getattr(g, 'geoms', []) if isinstance(p, Polygon)]
    out = []
    for p in polys:
        if p.is_empty or p.area < (tol*tol)*0.5: continue
        p = orient(p, sign=-1.0)
        out.append(ring_path(list(p.exterior.coords)))
        for r in p.interiors:
            if Polygon(r).area >= min_hole: out.append(ring_path(list(r.coords)))
    return ''.join(out)

mun = {c: path_of(g) for c, g in zip(codes, simp)}
dep = {}
for k, v in old['dep'].items():
    members = [g for c, g in zip(codes, simp) if c[:2] == k]
    dep[k] = {'n': v['n'], 'p': path_of(unary_union(members).buffer(0), 0.003) if members else ''}
out = {'w': old['w'], 'h': old['h'], 'proj': P, 'dep': dep, 'mun': mun}
s = json.dumps(out, ensure_ascii=False, separators=(',', ':'))
open(os.path.join(here, '..', 'data', 'mapa_colombia.json'), 'w', encoding='utf-8').write(s)
print('bytes', len(s), 'dep con trazo', sum(1 for d in dep.values() if d['p']))
