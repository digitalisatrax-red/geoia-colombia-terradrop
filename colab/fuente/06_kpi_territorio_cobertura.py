#@title 6 · KPI · Territorio y cobertura (CLC 2024) { display-mode: "form" }
K = {}
cent = gpd.GeoSeries([TERR_GEOM], crs=CRS_METRICO).to_crs(4326).iloc[0].centroid
off_ha = None
if ES_VEREDA:
    c_a = col(TERR, "area_ha")
    off_ha = num(TERR.iloc[0][c_a]) if c_a else None

K["territorio"] = {
    "nombre": NOM_TERR_TITULO, "tipo": "vereda" if ES_VEREDA else "municipio",
    "departamento": NOM_DPTO, "municipio": NOM_MUN, "vereda": NOM_VER or None,
    "codigo_dane_municipio": COD_MUN, "codigo_vereda": COD_VER or None,
    "area_ha": rd(AREA_T_HA, 1), "area_km2": rd(AREA_T_KM2, 2),
    "area_oficial_ha": rd(off_ha, 1) if off_ha else None,
    "perimetro_km": rd(TERR_GEOM.length / 1000, 1),
    "area_municipio_ha": rd(MUN_GEOM.area / 1e4, 1),
    "porcentaje_del_municipio": rd(AREA_T_HA / (MUN_GEOM.area / 1e4) * 100, 1) if ES_VEREDA else 100.0,
    "numero_veredas_municipio": int(len(ver_all)) if not ES_VEREDA else None,
    "centroide": {"lon": round(cent.x, 5), "lat": round(cent.y, 5)},
    "crs_metrico": CRS_METRICO,
}

# ---------------- cobertura ----------------
clc = D["clc2024"].copy()
CLC_OK = len(clc) > 0 and col(clc, "codigo") is not None
if CLC_OK:
    clc["codigo"] = texto_col(clc, "codigo").str.replace(r"\.0$", "", regex=True)
    clc["n1"], clc["n2"] = clc["codigo"].str[:1], clc["codigo"].str[:2]
    c_ley = col(clc, "leyenda")
    clc["leyenda"] = clc[c_ley].astype(str).str.strip() if c_ley else clc["codigo"]
    clc["ha"] = clc.geometry.area / 1e4
    TOTAL_CLC = clc["ha"].sum()

    n1 = clc.groupby("n1")["ha"].sum().reindex(list(CLC_N1)).fillna(0)
    nivel1 = [{"codigo": k, "nombre": CLC_N1[k], "ha": rd(v, 1), "porcentaje": rd(v / TOTAL_CLC * 100, 1), "color": CLC_COL[k]}
              for k, v in n1.items()]
    n2 = clc.groupby("n2")["ha"].sum().sort_values(ascending=False)
    nivel2 = [{"codigo": k, "nombre": CLC_N2.get(k, "Otra cobertura"), "ha": rd(v, 1), "porcentaje": rd(v / TOTAL_CLC * 100, 1)}
              for k, v in n2.items() if v > 0]
    g3 = clc.groupby("codigo").agg(ha=("ha", "sum"), parches=("ha", "size"), leyenda=("leyenda", "first")).sort_values("ha", ascending=False)
    nivel3 = [{"codigo": k, "nombre": r.leyenda, "ha": rd(r.ha, 1), "porcentaje": rd(r.ha / TOTAL_CLC * 100, 1),
               "parches": int(r.parches), "clase_nivel1": k[:1]} for k, r in g3.iterrows()]
    p = g3["ha"] / TOTAL_CLC
    p = p[p > 0]
    shannon = float(-(p * np.log(p)).sum())
    equit = shannon / math.log(len(p)) if len(p) > 1 else 0.0
    nat = clc[clc.n1.isin(NATURALES)]["ha"].sum()
    trans = clc[clc.n1.isin(("1", "2"))]["ha"].sum()
    bosque = clc[clc.n2 == "31"]
    ha_bosque = bosque["ha"].sum()
    if len(bosque):
        parches = list(unary_union(bosque.geometry).geoms) if unary_union(bosque.geometry).geom_type == "MultiPolygon" else [unary_union(bosque.geometry)]
        areas_p = sorted([q.area / 1e4 for q in parches], reverse=True)
        frag = {"parches": len(areas_p), "tamano_medio_ha": rd(float(np.mean(areas_p)), 1),
                "parche_mayor_ha": rd(areas_p[0], 1), "porcentaje_en_parche_mayor": rd(areas_p[0] / ha_bosque * 100, 1)}
    else:
        frag = {"parches": 0, "tamano_medio_ha": None, "parche_mayor_ha": None, "porcentaje_en_parche_mayor": None}
    dom = nivel3[0]
    pastos = clc[clc.n2 == "23"]["ha"].sum()
    cultivos = clc[clc.n2.isin(("21", "22"))]["ha"].sum()
    K["cobertura"] = {
        "anio": 2024, "escala": "1:100.000", "area_clasificada_ha": rd(TOTAL_CLC, 1),
        "porcentaje_territorio_con_dato": rd(TOTAL_CLC / AREA_T_HA * 100, 1),
        "nivel1": nivel1, "nivel2": nivel2, "nivel3": nivel3,
        "natural_seminatural_ha": rd(nat, 1), "natural_seminatural_pct": rd(nat / TOTAL_CLC * 100, 1),
        "transformada_ha": rd(trans, 1), "transformada_pct": rd(trans / TOTAL_CLC * 100, 1),
        "bosque_ha": rd(ha_bosque, 1), "bosque_pct": rd(ha_bosque / TOTAL_CLC * 100, 1), "bosque_fragmentacion": frag,
        "pastos_ha": rd(pastos, 1), "pastos_pct": rd(pastos / TOTAL_CLC * 100, 1),
        "cultivos_ha": rd(cultivos, 1), "cultivos_pct": rd(cultivos / TOTAL_CLC * 100, 1),
        "cobertura_dominante": {"codigo": dom["codigo"], "nombre": dom["nombre"], "porcentaje": dom["porcentaje"]},
        "numero_coberturas_nivel3": len(nivel3), "shannon": rd(shannon, 3), "equitatividad": rd(equit, 3),
    }
    print(f"Cobertura dominante: {dom['nombre']} ({fmt(dom['porcentaje'],1)} %) · natural/seminatural {fmt(nat/TOTAL_CLC*100,1)} % · bosque {fmt(ha_bosque,1)} ha")
else:
    TOTAL_CLC = 0
    K["cobertura"] = None
    print("⚠ Sin datos de coberturas CLC en el territorio: esa sección quedará vacía en el dashboard.")
