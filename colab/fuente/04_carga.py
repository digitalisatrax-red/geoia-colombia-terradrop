#@title 4 · Cargar las capas (ZIP de TerraDrop o APIs) { display-mode: "form" }
# ---------------- consulta a los servicios ArcGIS REST ----------------
def _post(url, datos, intentos=3, espera=60):
    ultimo = None
    for i in range(intentos):
        try:
            r = requests.post(url, data=datos, timeout=espera)
            r.raise_for_status()
            j = r.json()
            if "error" in j:
                raise RuntimeError(j["error"].get("message", "El servicio devolvió un error"))
            return j
        except Exception as e:      # reintento con espera creciente
            ultimo = e
            time.sleep(1.5 * (i + 1))
    raise ultimo

def _anillos(geom, tol0=0.0003, max_vertices=4000):
    """Polígono simplificado -> anillos Esri (exterior en sentido horario). Pocos vértices = consulta ligera."""
    tol, anillos = tol0, []
    for _ in range(7):
        g = geom.simplify(tol, preserve_topology=True)
        polis = [g] if g.geom_type == "Polygon" else [p for p in getattr(g, "geoms", []) if p.geom_type == "Polygon"]
        anillos, n = [], 0
        for p in polis:
            if p.is_empty:
                continue
            p = orient(p, sign=-1.0)
            for r in [p.exterior, *p.interiors]:
                c = [list(xy) for xy in r.coords]
                anillos.append(c)
                n += len(c)
        if anillos and n <= max_vertices:
            break
        tol *= 2.2
    return anillos

def _filtro_esri(geom, modo):
    if modo == "envolvente":
        x0, y0, x1, y1 = geom.bounds
        return "esriGeometryEnvelope", {"xmin": x0, "ymin": y0, "xmax": x1, "ymax": y1, "spatialReference": {"wkid": 4326}}
    return "esriGeometryPolygon", {"rings": _anillos(geom), "spatialReference": {"wkid": 4326}}

def _a_gdf(feats):
    if not feats:
        return vacio()
    return gpd.GeoDataFrame.from_features(feats, crs="EPSG:4326")

def consultar(capa, where="1=1", geom=None, url=None, page=None, spatial=None, extra=None):
    """Descarga una capa completa (paginada). geom = polígono shapely en EPSG:4326 para el filtro espacial."""
    s = SERV.get(capa, {})
    url = url or s["url"]
    page = page or s.get("page", 1000)
    spatial = s.get("spatial", False) if spatial is None else spatial
    feats, offset, modo = [], 0, "poligono"
    while True:
        datos = {"where": where, "outFields": "*", "outSR": 4326, "returnGeometry": "true", "f": "geojson",
                 "resultOffset": offset, "resultRecordCount": page}
        datos.update(extra or {})
        if spatial and geom is not None:
            tipo, esri = _filtro_esri(geom, modo)
            datos.update(geometry=json.dumps(esri), geometryType=tipo, inSR=4326, spatialRel="esriSpatialRelIntersects")
        try:
            j = _post(url, datos)
        except Exception:
            if spatial and geom is not None and modo == "poligono" and offset == 0:
                modo = "envolvente"      # el servicio no aceptó el polígono: se usa la envolvente
                continue
            raise
        got = j.get("features", [])
        feats += got
        mas = j.get("exceededTransferLimit") or (j.get("properties") or {}).get("exceededTransferLimit")
        if not got or (not mas and len(got) < page):
            break
        offset += len(got)
        if offset > 250000:
            break
    return _a_gdf(feats)

def cargar_api(cod_mun, cod_ver=""):
    cod_mun = str(cod_mun).strip().zfill(5)
    capas = {"municipio": consultar("municipio", f"num_dane='{cod_mun}'")}
    if len(capas["municipio"]) == 0:
        raise ValueError(f"No se encontró el municipio {cod_mun}. Revisa el código DANE (5 dígitos).")
    donde = f"cod_ver='{cod_ver}'" if cod_ver else f"cod_mpio='{cod_mun}'"
    capas["veredas"] = consultar("veredas", donde)
    if cod_ver and len(capas["veredas"]) == 0:
        raise ValueError(f"No se encontró la vereda {cod_ver}. Revisa el código (8 dígitos).")
    base = capas["veredas"] if cod_ver else capas["municipio"]
    geom = unary_union(base.geometry.make_valid())
    for c in CAPAS:
        if c in capas:
            continue
        print(f"  · {SERV[c]['nombre']} …", end=" ")
        capas[c] = consultar(c, geom=geom)
        print(len(capas[c]), "elementos")
    return capas, {"origen": "api", "cod_mun": cod_mun, "cod_ver": cod_ver}

# ---------------- ZIP de TerraDrop ----------------
def cargar_zip(ruta):
    z = zipfile.ZipFile(ruta)
    capas, cod_mun, cod_ver = {}, "", ""
    for n in z.namelist():
        b = os.path.basename(n)
        if not b.lower().endswith(".geojson") or b.lower().startswith("asignacion_"):
            continue
        for cid in sorted(CAPAS, key=len, reverse=True):
            if b.endswith(f"_{cid}.geojson"):
                m = re.match(r"^(\d{5})_", b)
                cod_mun = cod_mun or (m.group(1) if m else "")
                v = re.search(r"_v(\d{6,8})_", b)
                cod_ver = cod_ver or (v.group(1) if v else "")
                try:
                    capas[cid] = gpd.read_file(io.BytesIO(z.read(n)))
                except Exception:
                    capas[cid] = vacio()
                if capas[cid].crs is None:
                    capas[cid] = capas[cid].set_crs("EPSG:4326")
                capas[cid] = capas[cid].to_crs("EPSG:4326")
                break
    if "municipio" not in capas:
        raise ValueError("El ZIP no trae la capa de límite municipal (…_municipio.geojson). Descárgalo de nuevo con esa capa marcada.")
    for c in CAPAS:
        capas.setdefault(c, vacio())
    return capas, {"origen": "zip", "cod_mun": cod_mun, "cod_ver": cod_ver, "zip": os.path.basename(ruta)}

# ---------------- decidir la fuente ----------------
def _subir_zip():
    try:
        from google.colab import files
    except ImportError:
        return None
    print("Sube el ZIP de TerraDrop (o cancela para consultar las APIs con el código DANE)…")
    try:
        subido = files.upload()
    except Exception:
        return None
    for nombre in subido:
        if nombre.lower().endswith(".zip"):
            return nombre
    return None

ruta = RUTA_ZIP.strip() if RUTA_ZIP else ""
if ORIGEN in ("auto", "zip") and not (ruta and os.path.exists(ruta)):
    ruta = _subir_zip() or ""
if ORIGEN in ("auto", "zip") and ruta and os.path.exists(ruta):
    print("Leyendo ZIP:", ruta)
    CAPAS_RAW, FUENTE = cargar_zip(ruta)
    if CODIGO_MUNICIPIO.strip():
        FUENTE["cod_mun"] = CODIGO_MUNICIPIO.strip().zfill(5)
    if CODIGO_VEREDA.strip():
        FUENTE["cod_ver"] = CODIGO_VEREDA.strip()
elif ORIGEN in ("auto", "api") and CODIGO_MUNICIPIO.strip():
    print("Consultando las APIs oficiales para", CODIGO_MUNICIPIO.strip(), CODIGO_VEREDA.strip() or "(todo el municipio)")
    CAPAS_RAW, FUENTE = cargar_api(CODIGO_MUNICIPIO, CODIGO_VEREDA.strip())
else:
    raise SystemExit("No hay datos de entrada: sube el ZIP de TerraDrop o escribe CODIGO_MUNICIPIO (5 dígitos) en los parámetros y vuelve a ejecutar.")

print("\nCapas cargadas:")
for c in CAPAS:
    print(f"  {SERV[c]['nombre']:<38} {len(CAPAS_RAW[c]):>6} elementos")
