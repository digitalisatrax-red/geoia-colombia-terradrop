#@title 9 · KPI · Vías y accesibilidad { display-mode: "form" }
por_clase, partes, km_tot = [], [], 0.0
for cid, etiqueta in VIAS.items():
    g = D[cid]
    km = _km(g)
    km_tot += km
    por_clase.append({"id": cid, "nombre": etiqueta, "km": rd(km, 2), "tramos": int(len(g))})
    if len(g):
        gg = g[["geometry"]].copy()
        c_nm = col(g, "NOMBRE_GEOGRAFICO")
        gg["nombre"] = g[c_nm].astype(str).str.strip() if c_nm else ""
        gg["clase"] = cid
        partes.append(gg)
for d in por_clase:
    d["porcentaje"] = rd((d["km"] or 0) / km_tot * 100, 1) if km_tot else 0.0

VIAS_ALL = pd.concat(partes, ignore_index=True) if partes else vacio(CRS_METRICO)
VIAS_GEOM = unary_union(VIAS_ALL.geometry) if len(VIAS_ALL) else None

# accesibilidad: qué parte del territorio queda a <= d km de una vía
acceso = []
BUFFERS = {}
for d in DISTANCIAS_ACCESO_KM:
    if VIAS_GEOM is not None:
        b = VIAS_GEOM.buffer(d * 1000).intersection(TERR_GEOM)
        BUFFERS[d] = b
        ha = b.area / 1e4
    else:
        BUFFERS[d], ha = None, 0.0
    acceso.append({"distancia_km": d, "ha": rd(ha, 1), "porcentaje": rd(ha / AREA_T_HA * 100, 1)})

nombradas = []
if len(VIAS_ALL):
    v = VIAS_ALL[~VIAS_ALL["nombre"].str.lower().isin(["", "none", "nan", "null"])]
    for k, g in v.groupby("nombre"):
        nombradas.append({"nombre": titulo(k), "km": rd(_km(g), 2)})
    nombradas.sort(key=lambda d: -(d["km"] or 0))

pav = next((d["km"] for d in por_clase if d["id"] == "vias_pavimentadas"), 0) or 0
K["vias"] = {
    "total_km": rd(km_tot, 2), "tramos": int(sum(d["tramos"] for d in por_clase)),
    "densidad_km_km2": rd(km_tot / AREA_T_KM2, 3) if AREA_T_KM2 else None,
    "pavimentadas_pct": rd(pav / km_tot * 100, 1) if km_tot else 0.0,
    "por_clase": por_clase, "accesibilidad": acceso, "vias_nombradas": nombradas[:8],
    "territorio_sin_via_3km_pct": rd(100 - (acceso[-1]["porcentaje"] or 0), 1) if acceso else None,
    "nota": "Las vías provienen de la capa Interés Colombia (IGAC); sirven para lectura territorial, no para ingeniería. La clasificación es la de cada capa (pavimentadas, sin pavimentar, transitables en tiempo seco).",
}
print(f"Vías: {fmt(km_tot,1)} km · densidad {fmt(km_tot/AREA_T_KM2,2)} km/km² · pavimentadas {fmt(K['vias']['pavimentadas_pct'],1)} %")
for a in acceso:
    print(f"  a ≤ {a['distancia_km']} km de una vía: {fmt(a['porcentaje'],1)} % del territorio")
