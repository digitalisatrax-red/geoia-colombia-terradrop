#@title 11 · Lecturas automáticas, tarjetas KPI y kpis.json { display-mode: "form" }
T, C, A, H, V, X = K["territorio"], K["cobertura"], K["areas_protegidas"], K["hidrografia"], K["vias"], K["cruces"]
fecha = datetime.datetime.now().strftime("%Y-%m-%d")

# ---------- lecturas en lenguaje claro ----------
L = []
L.append(f"{T['nombre']} ocupa {fmt(T['area_ha'],1)} ha ({fmt(T['area_km2'],2)} km²) en {T['departamento']}"
         + (f" y equivale al {fmt(T['porcentaje_del_municipio'],1)} % del municipio de {T['municipio']}." if T["tipo"] == "vereda" else
            (f"; tiene {T['numero_veredas_municipio']} veredas registradas." if T.get("numero_veredas_municipio") else ".")))
if C:
    L.append(f"La cobertura dominante es «{C['cobertura_dominante']['nombre']}» ({fmt(C['cobertura_dominante']['porcentaje'],1)} % del área clasificada); "
             f"el {fmt(C['natural_seminatural_pct'],1)} % del territorio conserva coberturas naturales o seminaturales y el {fmt(C['transformada_pct'],1)} % está transformado (territorios artificializados y agrícolas).")
    if (C["bosque_ha"] or 0) > 0:
        f_ = C["bosque_fragmentacion"]
        L.append(f"Hay {fmt(C['bosque_ha'],1)} ha de bosque ({fmt(C['bosque_pct'],1)} %) repartidas en {f_['parches']} parche(s); el mayor reúne el {fmt(f_['porcentaje_en_parche_mayor'],1)} % del bosque.")
    L.append(f"Se identifican {C['numero_coberturas_nivel3']} coberturas de nivel 3; el índice de Shannon es {fmt(C['shannon'],2)} (equitatividad {fmt(C['equitatividad'],2)}).")
if A["hay_traslape"]:
    mayor = A["areas"][0]
    L.append(f"{A['numero_areas']} área(s) protegida(s) del RUNAP se traslapan con el territorio y cubren {fmt(A['protegida_ha'],1)} ha ({fmt(A['protegida_pct'],1)} %); la mayor es {mayor['nombre']} ({mayor['categoria']}).")
else:
    L.append("No se traslapa ninguna área protegida del RUNAP con el territorio.")
if (H["drenajes_km"] or 0) > 0:
    L.append(f"La capa de drenajes suma {fmt(H['drenajes_km'],1)} km, con una densidad de {fmt(H['densidad_drenaje_km_km2'],2)} km/km².")
else:
    L.append("La capa de drenajes consultada no registra cauces dentro del territorio.")
if (V["total_km"] or 0) > 0:
    ac = V["accesibilidad"]
    L.append(f"Hay {fmt(V['total_km'],1)} km de vías ({fmt(V['pavimentadas_pct'],1)} % pavimentadas) y el {fmt(ac[0]['porcentaje'],1)} % del territorio queda a ≤ {ac[0]['distancia_km']} km de una vía"
             + (f" ({fmt(ac[-1]['porcentaje'],1)} % a ≤ {ac[-1]['distancia_km']} km)." if len(ac) > 1 else "."))
else:
    L.append("La capa de vías consultada no registra vías dentro del territorio.")
if (X["vias_en_areas_protegidas_km"] or 0) > 0:
    L.append(f"{fmt(X['vias_en_areas_protegidas_km'],1)} km de vías atraviesan áreas protegidas.")
if X["bosque_cerca_de_vias"] and X["bosque_cerca_de_vias"][0]["porcentaje_del_bosque"] is not None:
    b0 = X["bosque_cerca_de_vias"][0]
    L.append(f"El {fmt(b0['porcentaje_del_bosque'],1)} % del bosque está a ≤ {b0['distancia_km']} km de una vía (accesibilidad al bosque).")
K["lecturas"] = L

# ---------- fuentes (formato de nota bajo gráficos y tablas) ----------
K["fuentes"] = {
    "limites": f"DANE (s. f.). Marco Geoestadístico Nacional: municipios y veredas [Servicio ArcGIS REST publicado por IDEAM]. https://visualizador.ideam.gov.co/",
    "cobertura": "IDEAM (2024). Mapa de coberturas de la tierra, metodología Corine Land Cover adaptada para Colombia, escala 1:100.000 [Servicio ArcGIS REST]. https://visualizador.ideam.gov.co/",
    "areas_protegidas": "Ministerio de Ambiente y Desarrollo Sostenible (s. f.). Registro Único Nacional de Áreas Protegidas (RUNAP) [Servicio ArcGIS REST]. https://geo.minambiente.gov.co/",
    "hidrografia": "Capa HIDROGRAFIA (ArcGIS Online) e Instituto Geográfico Agustín Codazzi (s. f.), Interés Colombia: ríos principales [Servicios ArcGIS REST].",
    "vias": "Instituto Geográfico Agustín Codazzi (s. f.). Interés Colombia: vías [Servicio ArcGIS REST, ArcGIS Online].",
    "procesamiento": f"Elaboración propia con GeoIA Colombia · TerraDrop. Áreas y longitudes calculadas en MAGNA-SIRGAS Origen Nacional ({CRS_METRICO}); consulta de los servicios y cálculo el {fecha}.",
}

# ---------- tarjetas listas para el dashboard ----------
def tarjeta(grupo, id_, titulo_, valor, unidad, detalle, fuente):
    texto = f"{fmt(valor, 1 if isinstance(valor, float) and abs(valor) < 1000 else 0)} {unidad}".strip() if num(valor) is not None else str(valor)
    return {"grupo": grupo, "id": id_, "titulo": titulo_, "valor": valor, "unidad": unidad, "valor_texto": texto, "detalle": detalle, "fuente": fuente}

TARJ = [
    tarjeta("territorio", "area", "Área del territorio", T["area_ha"], "ha", f"{fmt(T['area_km2'],2)} km² · perímetro {fmt(T['perimetro_km'],1)} km", "limites"),
]
if T["tipo"] == "vereda":
    TARJ.append(tarjeta("territorio", "peso_municipio", "Peso en el municipio", T["porcentaje_del_municipio"], "%", f"de {T['municipio']}", "limites"))
elif T.get("numero_veredas_municipio") is not None:
    TARJ.append(tarjeta("territorio", "veredas", "Veredas", T["numero_veredas_municipio"], "", "registradas en el municipio", "limites"))
if C:
    TARJ += [
        tarjeta("cobertura", "natural", "Cobertura natural y seminatural", C["natural_seminatural_pct"], "%", "bosques, vegetación, humedales y agua", "cobertura"),
        tarjeta("cobertura", "bosque", "Bosque", C["bosque_ha"], "ha", f"{fmt(C['bosque_pct'],1)} % del territorio · {C['bosque_fragmentacion']['parches']} parche(s)", "cobertura"),
        tarjeta("cobertura", "dominante", "Cobertura dominante", C["cobertura_dominante"]["nombre"], "", f"{fmt(C['cobertura_dominante']['porcentaje'],1)} % del área", "cobertura"),
        tarjeta("cobertura", "shannon", "Diversidad de coberturas", C["shannon"], "H′", f"{C['numero_coberturas_nivel3']} coberturas de nivel 3", "cobertura"),
    ]
TARJ += [
    tarjeta("areas_protegidas", "protegida_pct", "Territorio en áreas protegidas", A["protegida_pct"], "%", f"{fmt(A['protegida_ha'],1)} ha · {A['numero_areas']} área(s)", "areas_protegidas"),
    tarjeta("hidrografia", "drenajes_km", "Drenajes", H["drenajes_km"], "km", f"{H['drenajes_tramos']} tramos", "hidrografia"),
    tarjeta("hidrografia", "densidad", "Densidad de drenaje", H["densidad_drenaje_km_km2"], "km/km²", "longitud de drenajes por km²", "hidrografia"),
    tarjeta("vias", "total_km", "Vías", V["total_km"], "km", f"{fmt(V['densidad_km_km2'],2)} km/km²", "vias"),
    tarjeta("vias", "pavimentadas", "Vías pavimentadas", V["pavimentadas_pct"], "%", "del total de vías", "vias"),
]
for a_ in V["accesibilidad"]:
    TARJ.append(tarjeta("vias", f"acceso_{a_['distancia_km']}km", f"Territorio a ≤ {a_['distancia_km']} km de una vía", a_["porcentaje"], "%", f"{fmt(a_['ha'],1)} ha", "vias"))
TARJ.append(tarjeta("cruces", "vias_en_ap", "Vías dentro de áreas protegidas", X["vias_en_areas_protegidas_km"], "km", "cruce de vías × RUNAP", "areas_protegidas"))
if X["bosque_cerca_de_vias"]:
    b0 = X["bosque_cerca_de_vias"][0]
    TARJ.append(tarjeta("cruces", "bosque_cerca_vias", f"Bosque a ≤ {b0['distancia_km']} km de una vía", b0["porcentaje_del_bosque"], "%", f"{fmt(b0['ha'],1)} ha", "cobertura"))
K["tarjetas"] = TARJ

K["metadatos"] = {
    "titulo": f"Tablero territorial · {T['nombre']}", "generado": datetime.datetime.now().isoformat(timespec="seconds"),
    "generador": "GeoIA Colombia · TerraDrop · Colab KPI", "origen_datos": FUENTE.get("origen"), "crs_metrico": CRS_METRICO,
    "capas": {c: {"nombre": SERV[c]["nombre"], "fuente": SERV[c]["fuente"], "elementos_en_territorio": int(len(D[c]))} for c in CAPAS},
    "grupos_kpi": ["territorio", "cobertura", "areas_protegidas", "hidrografia", "vias", "cruces"],
}
print("\n".join("• " + l for l in L))
print(f"\n{len(TARJ)} tarjetas KPI · {len(K['veredas'])} veredas en la tabla")
