#@title 5 · Preparar el territorio (proyección, reparación y recorte) { display-mode: "form" }
COD_MUN = FUENTE.get("cod_mun") or ""
COD_VER = FUENTE.get("cod_ver") or ""

# --- reparar y proyectar a metros ---
RAW_M = {}
for c in CAPAS:
    g = limpiar(CAPAS_RAW[c], SERV[c]["kind"])
    RAW_M[c] = g.to_crs(CRS_METRICO) if len(g) else vacio(CRS_METRICO)

mun = RAW_M["municipio"]
if len(mun) == 0:
    raise SystemExit("La capa de límite municipal está vacía; no se puede continuar.")
mun_row = CAPAS_RAW["municipio"].iloc[0]
if not COD_MUN:
    COD_MUN = str(mun_row.get(col(CAPAS_RAW["municipio"], "num_dane"), "")).zfill(5)

# --- nombres ---
c_dpto = col(CAPAS_RAW["municipio"], "nom_dpto")
dpto_val = str(mun_row.get(c_dpto, "")).strip() if c_dpto else ""
if dpto_val.isdigit():
    dpto_val = DEPARTAMENTOS.get(dpto_val.zfill(2), dpto_val)
if not dpto_val or dpto_val.lower() == "none":
    dpto_val = DEPARTAMENTOS.get(COD_MUN[:2], "")
NOM_DPTO = titulo(dpto_val) if dpto_val.isupper() or dpto_val.islower() else dpto_val
NOM_MUN = titulo(str(mun_row.get(col(CAPAS_RAW["municipio"], "nom_mpio"), COD_MUN)))

# --- territorio de estudio: vereda (si hay) o municipio ---
ver_all = RAW_M["veredas"]
c_cv, c_nv = col(ver_all, "cod_ver"), col(ver_all, "nom_ver")
if COD_VER and len(ver_all) and c_cv:
    sel = ver_all[ver_all[c_cv].astype(str) == str(COD_VER)]
    TERR = sel if len(sel) else mun
    ES_VEREDA = len(sel) > 0
else:
    TERR, ES_VEREDA = mun, False
if ES_VEREDA:
    NOM_VER = titulo(str(TERR.iloc[0][c_nv])) if c_nv else COD_VER
    NOM_TERR = f"Vereda {NOM_VER} · {NOM_MUN}"
else:
    NOM_VER = ""
    NOM_TERR = NOM_MUN
if NOMBRE_PROYECTO.strip():
    NOM_TERR_TITULO = NOMBRE_PROYECTO.strip()
else:
    NOM_TERR_TITULO = NOM_TERR
TERR_GEOM = unary_union(TERR.geometry)
MUN_GEOM = unary_union(mun.geometry)
AREA_T_HA = TERR_GEOM.area / 1e4
AREA_T_KM2 = AREA_T_HA / 100

# --- recortar todas las capas al territorio ---
D = {}
for c in CAPAS:
    g = RAW_M[c]
    if c in ("municipio", "veredas"):
        D[c] = g
        continue
    if len(g) == 0:
        D[c] = g
        continue
    try:
        r_ = gpd.clip(g, TERR_GEOM, keep_geom_type=True)
    except Exception:
        r_ = g[g.intersects(TERR_GEOM)].copy()
        r_["geometry"] = r_.geometry.intersection(TERR_GEOM)
    D[c] = limpiar(r_, SERV[c]["kind"])

# --- veredas que se tabulan: la elegida, o todas las del municipio ---
VER_M = TERR if ES_VEREDA else ver_all
if len(VER_M) and c_cv:
    VER_M = VER_M.rename(columns={c_cv: "cod_ver"}).copy()
    VER_M["nom_ver"] = VER_M[c_nv].astype(str).map(titulo) if c_nv else VER_M["cod_ver"]
else:
    VER_M = vacio(CRS_METRICO)

print(f"Territorio: {NOM_TERR_TITULO}  ({'vereda ' + COD_VER if ES_VEREDA else 'municipio ' + COD_MUN})  · {NOM_DPTO}")
print(f"Área calculada: {fmt(AREA_T_HA, 1)} ha  ·  {fmt(AREA_T_KM2, 2)} km²  ·  veredas a tabular: {len(VER_M)}")
for c in CAPAS[2:]:
    print(f"  {SERV[c]['nombre']:<38} {len(D[c]):>6} fragmentos dentro del territorio")
