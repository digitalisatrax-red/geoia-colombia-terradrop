#@title 3 · Catálogo de capas y utilidades { display-mode: "form" }
IDEAM = "https://visualizador.ideam.gov.co/gisserver/rest/services"
INTERES = "https://services2.arcgis.com/RVvWzU3lgJISqdke/arcgis/rest/services/Interes_Colombia/FeatureServer"

# Mismo catálogo que usa TerraDrop (descargas.html). spatial=True -> se filtra con el polígono del territorio.
SERV = {
    "municipio":           dict(nombre="Límite municipal", kind="poly", page=1000, spatial=False,
                                fuente="DANE · Marco Geoestadístico Nacional (vía IDEAM)", url=IDEAM + "/Entidades_Territoriales/FeatureServer/2/query"),
    "veredas":             dict(nombre="Veredas DANE", kind="poly", page=1000, spatial=False,
                                fuente="DANE · Veredas (vía IDEAM)", url=IDEAM + "/Entidades_Territoriales/FeatureServer/5/query"),
    "runap":               dict(nombre="Áreas protegidas (RUNAP)", kind="poly", page=500, spatial=True,
                                fuente="MinAmbiente · RUNAP (OTL Área protegida)", url="https://geo.minambiente.gov.co/server/rest/services/OTL/OTL_Area_Protegida/FeatureServer/0/query"),
    "vias_pavimentadas":   dict(nombre="Vías pavimentadas", kind="line", page=1000, spatial=True,
                                fuente="IGAC · Interés Colombia", url=INTERES + "/16/query"),
    "vias_sin_pavimentar": dict(nombre="Vías sin pavimentar", kind="line", page=1000, spatial=True,
                                fuente="IGAC · Interés Colombia", url=INTERES + "/15/query"),
    "vias_tiempo_seco":    dict(nombre="Vías transitables en tiempo seco", kind="line", page=1000, spatial=True,
                                fuente="IGAC · Interés Colombia", url=INTERES + "/14/query"),
    "drenajes":            dict(nombre="Drenajes (hidrografía)", kind="line", page=1000, spatial=True,
                                fuente="Capa HIDROGRAFIA · ArcGIS Online", url="https://services.arcgis.com/vC1CdlKWEAtuT38d/ArcGIS/rest/services/HIDROGRAFIA/FeatureServer/0/query"),
    "rios_principales":    dict(nombre="Ríos principales", kind="line", page=1000, spatial=True,
                                fuente="IGAC · Interés Colombia (no es la red completa)", url=INTERES + "/8/query"),
    "clc2024":             dict(nombre="Coberturas de la tierra CLC 2024", kind="poly", page=1000, spatial=True,
                                fuente="IDEAM · Corine Land Cover 1:100.000", url=IDEAM + "/Estado_Cobertura_Tierra/MapServer/10/query"),
}
URL_DEPARTAMENTOS = IDEAM + "/Entidades_Territoriales/FeatureServer/4/query"
CAPAS = list(SERV)
VIAS = {"vias_pavimentadas": "Pavimentadas", "vias_sin_pavimentar": "Sin pavimentar", "vias_tiempo_seco": "Transitables solo en tiempo seco"}

CRS_METRICO = "EPSG:9377"   # MAGNA-SIRGAS / Origen-Nacional
try:
    import pyproj
    pyproj.CRS.from_user_input(CRS_METRICO)
except Exception:
    CRS_METRICO = "EPSG:3116"  # respaldo (MAGNA-SIRGAS / Colombia Bogotá)

# Corine Land Cover Colombia: niveles 1 y 2 (el nivel 3 viene en la columna "leyenda" de la capa)
CLC_N1 = {"1": "Territorios artificializados", "2": "Territorios agrícolas", "3": "Bosques y áreas seminaturales",
          "4": "Áreas húmedas", "5": "Superficies de agua"}
CLC_N2 = {"11": "Zonas urbanizadas", "12": "Zonas industriales o comerciales y redes de comunicación",
          "13": "Zonas de extracción minera e hidrocarburos y escombreras", "14": "Zonas verdes artificializadas no agrícolas",
          "21": "Cultivos transitorios", "22": "Cultivos permanentes", "23": "Pastos", "24": "Áreas agrícolas heterogéneas",
          "31": "Bosques", "32": "Vegetación herbácea y/o arbustiva", "33": "Áreas abiertas, sin o con poca vegetación",
          "41": "Áreas húmedas continentales", "42": "Áreas húmedas costeras", "51": "Aguas continentales", "52": "Aguas marítimas"}
CLC_COL = {"1": "#d95a5a", "2": "#e8c34b", "3": "#3fa56b", "4": "#7fc4b8", "5": "#4d8fe8"}   # mismos colores de TerraDrop
NATURALES = ("3", "4", "5")   # cobertura natural y seminatural = bosques/seminaturales + húmedas + agua

# Dominios codificados del RUNAP (servicio de MinAmbiente)
RUNAP_CAT = {3: ("Público", "Vía Parque", True), 4: ("Público", "Parque Natural Regional", False),
             5: ("Público", "Área Natural Única", True), 6: ("Público", "Distrito de Manejo Integrado", False),
             7: ("Privado", "Reserva Natural de la Sociedad Civil", False), 8: ("Público", "Reserva Forestal Protectora", False),
             9: ("Público", "Santuario de Flora", True), 10: ("Público", "Reserva Natural", True),
             11: ("Público", "Distrito de Conservación de Suelos", False), 12: ("Público", "Área de Recreación", False),
             13: ("Público", "Santuario de Flora y Fauna", True), 14: ("Público", "Parque Nacional Natural", True),
             15: ("Público", "Santuario de Fauna", True)}
RUNAP_ESTADO = {42: "Inscrita", 43: "Registrada"}
RUNAP_AMBITO = {63: "Nacional", 64: "Local", 65: "Regional"}
DEPARTAMENTOS = {"05": "Antioquia", "08": "Atlántico", "11": "Bogotá D.C.", "13": "Bolívar", "15": "Boyacá", "17": "Caldas",
                 "18": "Caquetá", "19": "Cauca", "20": "Cesar", "23": "Córdoba", "25": "Cundinamarca", "27": "Chocó",
                 "41": "Huila", "44": "La Guajira", "47": "Magdalena", "50": "Meta", "52": "Nariño", "54": "Norte de Santander",
                 "63": "Quindío", "66": "Risaralda", "68": "Santander", "70": "Sucre", "73": "Tolima", "76": "Valle del Cauca",
                 "81": "Arauca", "85": "Casanare", "86": "Putumayo", "88": "San Andrés, Providencia y Santa Catalina",
                 "91": "Amazonas", "94": "Guainía", "95": "Guaviare", "97": "Vaupés", "99": "Vichada"}

# ---------- utilidades ----------
def col(gdf, *nombres):
    """Devuelve el nombre real de la primera columna que exista (sin distinguir mayúsculas)."""
    bajo = {c.lower(): c for c in gdf.columns}
    for n in nombres:
        if n.lower() in bajo:
            return bajo[n.lower()]
    return None

def vacio(crs="EPSG:4326"):
    return gpd.GeoDataFrame({"geometry": []}, geometry="geometry", crs=crs)

def sin_tildes(s):
    return "".join(c for c in unicodedata.normalize("NFD", str(s)) if unicodedata.category(c) != "Mn")

def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", sin_tildes(s).lower()).strip("_") or "territorio"

def titulo(s):
    s = str(s or "").strip()
    peq = {"de", "del", "la", "las", "el", "los", "y", "en"}
    return " ".join(w.lower() if (i and w.lower() in peq) else w.capitalize() for i, w in enumerate(s.lower().split()))

def num(x):
    """None si no es un número finito."""
    try:
        x = float(x)
    except (TypeError, ValueError):
        return None
    return None if (math.isnan(x) or math.isinf(x)) else x

def rd(x, n=1):
    x = num(x)
    return None if x is None else round(x, n)

def fmt(x, dec=0):
    """Formato colombiano: 1.234,5"""
    x = num(x)
    if x is None:
        return "—"
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

def limpiar(gdf, tipo):
    """Repara geometrías y deja solo polígonos (tipo='poly') o líneas (tipo='line')."""
    if gdf is None or len(gdf) == 0:
        return vacio(gdf.crs if gdf is not None and gdf.crs else "EPSG:4326")
    g = gdf[gdf.geometry.notna() & ~gdf.geometry.is_empty].copy()
    if len(g) == 0:
        return vacio(gdf.crs)
    g["geometry"] = g.geometry.make_valid()
    g = g.explode(index_parts=False)
    g = g[g.geom_type == ("Polygon" if tipo == "poly" else "LineString")]
    return g[~g.geometry.is_empty].reset_index(drop=True)

def texto_col(gdf, nombre):
    c = col(gdf, nombre)
    return gdf[c].astype(str).str.strip() if c else pd.Series([""] * len(gdf), index=gdf.index)

print("Catálogo listo · CRS métrico:", CRS_METRICO, "·", len(SERV), "capas")
