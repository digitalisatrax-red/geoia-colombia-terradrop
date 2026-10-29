#@title 10 · KPI · Cruces entre capas y tabla por vereda { display-mode: "form" }
def inter(a, b):
    """Intersección tolerante a geometrías problemáticas."""
    if a is None or b is None or a.is_empty or b.is_empty:
        return None
    try:
        return a.intersection(b)
    except Exception:
        return shapely.make_valid(a).intersection(shapely.make_valid(b))

def km_de(g):
    return 0.0 if g is None or g.is_empty else g.length / 1000

def ha_de(g):
    return 0.0 if g is None or g.is_empty else g.area / 1e4

DR_GEOM = unary_union(D["drenajes"].geometry) if len(D["drenajes"]) else None
BOSQUE_GEOM = unary_union(bosque.geometry) if CLC_OK and len(bosque) else None
NAT_GEOM = unary_union(clc[clc.n1.isin(NATURALES)].geometry) if CLC_OK and (clc.n1.isin(NATURALES)).any() else None

cr = {}
cr["vias_en_areas_protegidas_km"] = rd(km_de(inter(VIAS_GEOM, AP_GEOM)), 2)
cr["drenajes_en_areas_protegidas_km"] = rd(km_de(inter(DR_GEOM, AP_GEOM)), 2)
cr["bosque_en_areas_protegidas_ha"] = rd(ha_de(inter(BOSQUE_GEOM, AP_GEOM)), 1)
bosque_ha_v = (K["cobertura"] or {}).get("bosque_ha") or 0
cr["bosque_protegido_pct"] = rd(cr["bosque_en_areas_protegidas_ha"] / bosque_ha_v * 100, 1) if bosque_ha_v else None
cr["natural_en_areas_protegidas_ha"] = rd(ha_de(inter(NAT_GEOM, AP_GEOM)), 1)
cr["drenajes_en_bosque_km"] = rd(km_de(inter(DR_GEOM, BOSQUE_GEOM)), 2)
cr["vias_en_bosque_km"] = rd(km_de(inter(VIAS_GEOM, BOSQUE_GEOM)), 2)
cerca = []
for d in DISTANCIAS_ACCESO_KM:
    ha = ha_de(inter(BOSQUE_GEOM, BUFFERS.get(d)))
    cerca.append({"distancia_km": d, "ha": rd(ha, 1), "porcentaje_del_bosque": rd(ha / bosque_ha_v * 100, 1) if bosque_ha_v else None})
cr["bosque_cerca_de_vias"] = cerca
cr["nota"] = "Cruces espaciales de lectura territorial: no son medidas de presión ni de amenaza por sí mismas."
K["cruces"] = cr
print("Cruces:", {k: v for k, v in cr.items() if k not in ("nota", "bosque_cerca_de_vias")})
for c_ in cerca:
    print(f"  bosque a ≤ {c_['distancia_km']} km de una vía: {fmt(c_['ha'],1)} ha ({fmt(c_['porcentaje_del_bosque'],1)} % del bosque)")

# ---------------- tabla por vereda ----------------
def tabla_veredas():
    if len(VER_M) == 0:
        return pd.DataFrame()
    v = VER_M[["cod_ver", "nom_ver", "geometry"]].copy()
    v["cod_ver"] = v["cod_ver"].astype(str)
    base = pd.DataFrame({"cod_ver": v["cod_ver"].values, "vereda": v["nom_ver"].values, "area_ha": v.geometry.area.values / 1e4})
    c_ao = col(VER_M, "area_ha")
    if c_ao:
        base["area_oficial_ha"] = pd.to_numeric(VER_M[c_ao], errors="coerce").values
    base = base.set_index("cod_ver")

    def sobre(layer, cols, tipo):
        if layer is None or len(layer) == 0:
            return None
        cols = [c for c in cols if c in layer.columns]
        try:
            o = gpd.overlay(layer[cols + ["geometry"]], v[["cod_ver", "geometry"]], how="intersection", keep_geom_type=True)
        except Exception:
            return None
        return limpiar(o, tipo)

    ser = lambda s: s.reindex(base.index).fillna(0.0) if s is not None else pd.Series(0.0, index=base.index)

    # coberturas
    if CLC_OK:
        o = sobre(clc, ["n1", "n2", "leyenda"], "poly")
        if o is not None and len(o):
            o["ha"] = o.geometry.area / 1e4
            tot = o.groupby("cod_ver")["ha"].sum()
            base["pct_natural"] = (ser(o[o.n1.isin(NATURALES)].groupby("cod_ver")["ha"].sum()) / ser(tot).replace(0, np.nan) * 100).round(1)
            base["bosque_ha"] = ser(o[o.n2 == "31"].groupby("cod_ver")["ha"].sum()).round(1)
            base["bosque_pct"] = (base["bosque_ha"] / ser(tot).replace(0, np.nan) * 100).round(1)
            g = o.groupby(["cod_ver", "leyenda"])["ha"].sum().reset_index().sort_values("ha", ascending=False).drop_duplicates("cod_ver").set_index("cod_ver")
            base["cobertura_dominante"] = g["leyenda"].reindex(base.index)
            base["dominante_pct"] = (g["ha"].reindex(base.index) / ser(tot).replace(0, np.nan) * 100).round(1)
    # áreas protegidas
    if AP_GEOM is not None:
        o = sobre(gpd.GeoDataFrame({"geometry": [AP_GEOM]}, crs=CRS_METRICO), [], "poly")
        s = o.assign(ha=o.geometry.area / 1e4).groupby("cod_ver")["ha"].sum() if o is not None and len(o) else None
    else:
        s = None
    base["protegida_ha"] = ser(s).round(1)
    base["protegida_pct"] = (base["protegida_ha"] / base["area_ha"] * 100).round(1)
    # vías y drenajes
    o = sobre(VIAS_ALL, ["clase"], "line") if len(VIAS_ALL) else None
    if o is not None and len(o):
        o["km"] = o.geometry.length / 1000
        base["vias_km"] = ser(o.groupby("cod_ver")["km"].sum()).round(2)
        base["vias_pavimentadas_km"] = ser(o[o.clase == "vias_pavimentadas"].groupby("cod_ver")["km"].sum()).round(2)
    else:
        base["vias_km"], base["vias_pavimentadas_km"] = 0.0, 0.0
    base["densidad_vias_km_km2"] = (base["vias_km"] / (base["area_ha"] / 100)).round(3)
    o = sobre(D["drenajes"], [], "line") if len(D["drenajes"]) else None
    base["drenajes_km"] = ser(o.assign(km=o.geometry.length / 1000).groupby("cod_ver")["km"].sum() if o is not None and len(o) else None).round(2)
    base["densidad_drenaje_km_km2"] = (base["drenajes_km"] / (base["area_ha"] / 100)).round(3)
    base["area_ha"] = base["area_ha"].round(1)
    return base.reset_index().sort_values("area_ha", ascending=False).reset_index(drop=True)

TAB_VEREDAS = tabla_veredas()
K["veredas"] = json.loads(TAB_VEREDAS.where(TAB_VEREDAS.notna(), None).to_json(orient="records", force_ascii=False)) if len(TAB_VEREDAS) else []
print(f"Tabla por vereda: {len(TAB_VEREDAS)} fila(s)")
if len(TAB_VEREDAS):
    print(TAB_VEREDAS.head(8).to_string(index=False))
