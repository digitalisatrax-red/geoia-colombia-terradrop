#@title 8 · KPI · Hidrografía { display-mode: "form" }
def _km(g):
    return float(g.length.sum()) / 1000 if len(g) else 0.0

dr, rp = D["drenajes"].copy(), D["rios_principales"].copy()
km_dr, km_rp = _km(dr), _km(rp)

por_tipo = []
if len(dr):
    c_t = col(dr, "LAYER")
    dr["tipo"] = texto_col(dr, "LAYER") if c_t else "s/d"
    for k, g in dr.groupby("tipo"):
        por_tipo.append({"codigo": k, "km": rd(_km(g), 2), "tramos": int(len(g))})
    por_tipo.sort(key=lambda d: -(d["km"] or 0))

def _top_nombres(gdf, campo, n=10):
    if len(gdf) == 0 or col(gdf, campo) is None:
        return []
    g = gdf.copy()
    g["_n"] = g[col(g, campo)].astype(str).str.strip()
    g = g[(g["_n"] != "") & (~g["_n"].str.lower().isin(["none", "nan", "null"]))]
    out = [{"nombre": titulo(k), "km": rd(_km(x), 2)} for k, x in g.groupby("_n")]
    return sorted(out, key=lambda d: -(d["km"] or 0))[:n]

agua_ha = 0.0
if CLC_OK:
    agua_ha = float(clc[clc.n1 == "5"]["ha"].sum())
K["hidrografia"] = {
    "drenajes_km": rd(km_dr, 2), "drenajes_tramos": int(len(dr)),
    "densidad_drenaje_km_km2": rd(km_dr / AREA_T_KM2, 3) if AREA_T_KM2 else None,
    "por_tipo": por_tipo, "drenajes_nombrados": _top_nombres(dr, "NMG"),
    "rios_principales_km": rd(km_rp, 2), "rios_principales": _top_nombres(rp, "Name"),
    "cuerpos_agua_clc_ha": rd(agua_ha, 1), "cuerpos_agua_clc_pct": rd(agua_ha / AREA_T_HA * 100, 2),
    "nota": "La capa de drenajes es la hidrografía disponible en ArcGIS Online (no es la red hídrica oficial IDEAM completa); los ríos principales de Interés Colombia son solo una selección.",
}
print(f"Drenajes: {fmt(km_dr,1)} km · densidad {fmt(km_dr/AREA_T_KM2,2)} km/km² · ríos principales: {fmt(km_rp,1)} km · agua (CLC): {fmt(agua_ha,1)} ha")
