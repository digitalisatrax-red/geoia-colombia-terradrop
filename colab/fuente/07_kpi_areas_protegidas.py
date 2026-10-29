#@title 7 · KPI · Áreas protegidas (RUNAP) { display-mode: "form" }
def _dec(v, dic, defecto="Sin dato"):
    try:
        return dic.get(int(float(v)), defecto)
    except (TypeError, ValueError):
        t = str(v).strip()
        return t if t and t.lower() != "none" else defecto

ap = D["runap"].copy()
AP_GEOM = None
if len(ap):
    c_nom, c_cat = col(ap, "uab_nombre_area_protegida", "nombre"), col(ap, "uab_categoria")
    c_est, c_amb = col(ap, "uab_estado"), col(ap, "uab_ambito_gestion")
    c_tot = col(ap, "area_total_ha")
    ap["nombre"] = ap[c_nom].astype(str).str.strip().map(titulo) if c_nom else "Área protegida"
    def _cat(v):
        try:
            return RUNAP_CAT[int(float(v))]
        except (KeyError, TypeError, ValueError):
            return ("Sin dato", str(v), False)
    cats = ap[c_cat].map(_cat) if c_cat else pd.Series([("Sin dato", "Sin dato", False)] * len(ap), index=ap.index)
    ap["naturaleza"] = cats.map(lambda t: t[0]); ap["categoria"] = cats.map(lambda t: t[1]); ap["spnn"] = cats.map(lambda t: t[2])
    ap["estado"] = ap[c_est].map(lambda v: _dec(v, RUNAP_ESTADO)) if c_est else "Sin dato"
    ap["ambito"] = ap[c_amb].map(lambda v: _dec(v, RUNAP_AMBITO)) if c_amb else "Sin dato"
    ap["total_ha"] = pd.to_numeric(ap[c_tot], errors="coerce") if c_tot else np.nan
    AP_GEOM = unary_union(ap.geometry)
    ap_ha = AP_GEOM.area / 1e4
    por_area = []
    for (nombre, categoria), g in ap.groupby(["nombre", "categoria"]):
        gm = unary_union(g.geometry)
        ha = gm.area / 1e4
        tot = num(g["total_ha"].max())
        por_area.append({"nombre": nombre, "categoria": categoria, "naturaleza": g["naturaleza"].iloc[0], "ambito": g["ambito"].iloc[0],
                         "estado": g["estado"].iloc[0], "sistema_parques_nacionales": bool(g["spnn"].iloc[0]),
                         "ha_en_territorio": rd(ha, 1), "porcentaje_del_territorio": rd(ha / AREA_T_HA * 100, 2),
                         "area_total_ha": rd(tot, 1), "porcentaje_del_area_en_territorio": rd(ha / tot * 100, 1) if tot else None})
    por_area.sort(key=lambda d: -(d["ha_en_territorio"] or 0))
    def _agr(campo):
        out = []
        for k, g in ap.groupby(campo):
            ha = unary_union(g.geometry).area / 1e4
            out.append({"nombre": k, "ha": rd(ha, 1), "porcentaje_del_territorio": rd(ha / AREA_T_HA * 100, 2),
                        "numero_areas": int(g["nombre"].nunique())})
        return sorted(out, key=lambda d: -(d["ha"] or 0))
    K["areas_protegidas"] = {
        "hay_traslape": True, "numero_areas": int(ap["nombre"].nunique()),
        "protegida_ha": rd(ap_ha, 1), "protegida_pct": rd(ap_ha / AREA_T_HA * 100, 1),
        "por_categoria": _agr("categoria"), "por_ambito": _agr("ambito"), "por_naturaleza": _agr("naturaleza"),
        "areas": por_area,
    }
    print(f"{K['areas_protegidas']['numero_areas']} área(s) protegida(s) · {fmt(ap_ha,1)} ha ({fmt(ap_ha/AREA_T_HA*100,1)} % del territorio)")
else:
    K["areas_protegidas"] = {"hay_traslape": False, "numero_areas": 0, "protegida_ha": 0.0, "protegida_pct": 0.0,
                             "por_categoria": [], "por_ambito": [], "por_naturaleza": [], "areas": []}
    print("Sin áreas protegidas del RUNAP que se traslapen con el territorio.")
