#@title 12 · Exportar kpis.json, tablas CSV y GeoJSON livianos { display-mode: "form" }
OUT = os.path.join(CARPETA_SALIDA, f"{COD_VER or COD_MUN}_{slug(NOM_TERR)}")
for sub in ("", "geojson", "tablas"):
    os.makedirs(os.path.join(OUT, sub), exist_ok=True)

def redondear(o, n=5):
    if isinstance(o, float):
        return round(o, n)
    if isinstance(o, list):
        return [redondear(x, n) for x in o]
    if isinstance(o, dict):
        return {k: redondear(v, n) for k, v in o.items()}
    return o

def ligero(gdf, columnas, tol_m, max_kb=1200):
    """GeoJSON en WGS84, simplificado y con 5 decimales; sube la tolerancia hasta caber en max_kb."""
    if gdf is None or len(gdf) == 0:
        return {"type": "FeatureCollection", "features": []}
    cols = [c for c in columnas if c in gdf.columns]
    for _ in range(7):
        g = gdf[cols + ["geometry"]].copy()
        g["geometry"] = g.geometry.simplify(tol_m, preserve_topology=True)
        g = g[~g.geometry.is_empty].to_crs(4326)
        fc = redondear(json.loads(g.to_json(drop_id=True)))
        if len(json.dumps(fc, ensure_ascii=False)) / 1024 <= max_kb:
            break
        tol_m *= 1.8
    return fc

x0, y0, x1, y1 = TERR_GEOM.bounds
TOL = max(3.0, math.hypot(x1 - x0, y1 - y0) / 1500)   # metros

capas_geo = {}
t = TERR.dissolve().reset_index(drop=True)
t["nombre"], t["tipo"], t["area_ha"] = NOM_TERR_TITULO, K["territorio"]["tipo"], K["territorio"]["area_ha"]
capas_geo["territorio"] = ligero(t, ["nombre", "tipo", "area_ha"], TOL / 2)
if ES_VEREDA:
    m_ = mun.copy(); m_["nombre"] = NOM_MUN
    capas_geo["municipio"] = ligero(m_, ["nombre"], TOL)
if len(VER_M):
    vv = VER_M.copy(); vv["cod_ver"] = vv["cod_ver"].astype(str)
    if len(TAB_VEREDAS):
        vv = vv.merge(TAB_VEREDAS.drop(columns=["vereda"]), on="cod_ver", how="left")
    capas_geo["veredas"] = ligero(vv, [c for c in vv.columns if c != "geometry"], TOL)
if CLC_OK:
    cc = clc.dissolve(by="codigo", aggfunc={"leyenda": "first", "n1": "first", "ha": "sum"}).reset_index()
    cc["color"] = cc["n1"].map(CLC_COL); cc["ha"] = cc["ha"].round(1)
    capas_geo["coberturas"] = ligero(cc, ["codigo", "leyenda", "n1", "color", "ha"], TOL)
if AP_GEOM is not None:
    capas_geo["areas_protegidas"] = ligero(ap, ["nombre", "categoria", "naturaleza", "ambito", "estado"], TOL)
if len(VIAS_ALL):
    va = VIAS_ALL.copy(); va["clase_nombre"] = va["clase"].map(VIAS)
    capas_geo["vias"] = ligero(va, ["clase", "clase_nombre", "nombre"], TOL / 2)
if len(D["drenajes"]):
    d_ = D["drenajes"].copy()
    capas_geo["drenajes"] = ligero(d_, ["tipo", "NMG"], TOL / 2)
if len(D["rios_principales"]):
    capas_geo["rios_principales"] = ligero(D["rios_principales"], ["Name"], TOL / 2)

ARCH_GEO = {}
for nombre, fc in capas_geo.items():
    ruta_ = os.path.join(OUT, "geojson", f"{nombre}.geojson")
    with open(ruta_, "w", encoding="utf-8") as f:
        json.dump(fc, f, ensure_ascii=False, separators=(",", ":"))
    ARCH_GEO[nombre] = {"archivo": f"geojson/{nombre}.geojson", "elementos": len(fc["features"]), "kb": round(os.path.getsize(ruta_) / 1024)}
K["archivos_geojson"] = ARCH_GEO

# ---- tablas CSV ----
def csv(nombre, df):
    if df is not None and len(df):
        df.to_csv(os.path.join(OUT, "tablas", nombre), index=False, encoding="utf-8-sig")

if C:
    csv("cobertura_nivel1.csv", pd.DataFrame(C["nivel1"]).drop(columns=["color"]))
    csv("cobertura_nivel2.csv", pd.DataFrame(C["nivel2"]))
    csv("cobertura_nivel3.csv", pd.DataFrame(C["nivel3"]))
csv("areas_protegidas.csv", pd.DataFrame(A["areas"]))
csv("hidrografia_tipos.csv", pd.DataFrame(H["por_tipo"]))
csv("hidrografia_nombrados.csv", pd.DataFrame(H["drenajes_nombrados"]))
csv("rios_principales.csv", pd.DataFrame(H["rios_principales"]))
csv("vias_clases.csv", pd.DataFrame(V["por_clase"]))
csv("accesibilidad.csv", pd.DataFrame(V["accesibilidad"]))
csv("veredas.csv", TAB_VEREDAS)
csv("tarjetas_kpi.csv", pd.DataFrame(K["tarjetas"]))

with open(os.path.join(OUT, "kpis.json"), "w", encoding="utf-8") as f:
    json.dump(K, f, ensure_ascii=False, indent=2, default=str)

print("Carpeta de salida:", OUT)
for n, i in ARCH_GEO.items():
    print(f"  geojson/{n}.geojson · {i['elementos']} elementos · {i['kb']} kB")
print("  kpis.json ·", round(os.path.getsize(os.path.join(OUT, 'kpis.json')) / 1024), "kB")
