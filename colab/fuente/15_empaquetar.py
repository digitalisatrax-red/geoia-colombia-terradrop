#@title 15 · Empaquetar y descargar { display-mode: "form" }
LEEME = f"""GeoIA Colombia · TerraDrop → Dashboard en Lovable
Territorio: {NOM_TERR_TITULO} ({NOM_DPTO}) · generado {fecha}

CONTENIDO
- prompt_lovable_corto.md : primer mensaje para Lovable (estructura general).
- prompt_lovable.md       : prompt completo con secciones, estilo, mapa y criterios de aceptación.
- kpis.json               : indicadores (tarjetas, coberturas, áreas protegidas, hidrografía, vías, cruces, veredas, lecturas, fuentes).
- geojson/                : territorio y capas livianas para el mapa.
- tablas/                 : tablas CSV de cada grupo de KPI.
- mapa_ubicacion.png      : mapa de ubicación para la portada.

CÓMO USARLO EN LOVABLE
1. Crea un proyecto nuevo en https://lovable.dev y pega prompt_lovable_corto.md.
2. Arrastra al chat kpis.json, la carpeta geojson/ y mapa_ubicacion.png (o súbelos a public/data y public/img).
3. Cuando la estructura esté lista, pega prompt_lovable.md para afinar cada sección.
4. Revisa que las cifras coincidan con la sección «Valores de referencia» del prompt.

NOTAS
- Áreas y longitudes calculadas en {CRS_METRICO}. Las capas son de lectura territorial, no de ingeniería ni de linderos legales.
- Revisa la vigencia de cada fuente en la página «Fuentes y calidad» de TerraDrop.
"""
with open(os.path.join(OUT, "LEEME.txt"), "w", encoding="utf-8") as f:
    f.write(LEEME)

ZIP_SALIDA = os.path.join(CARPETA_SALIDA, f"paquete_lovable_{COD_VER or COD_MUN}_{slug(NOM_TERR)}.zip")
with zipfile.ZipFile(ZIP_SALIDA, "w", zipfile.ZIP_DEFLATED) as z:
    for raiz, _, archivos in os.walk(OUT):
        for a in archivos:
            p = os.path.join(raiz, a)
            z.write(p, os.path.relpath(p, OUT))
print(f"Paquete listo: {ZIP_SALIDA} ({os.path.getsize(ZIP_SALIDA) / 1024:.0f} kB)")
for raiz, _, archivos in os.walk(OUT):
    for a in sorted(archivos):
        print("  ", os.path.relpath(os.path.join(raiz, a), OUT))
try:
    from google.colab import files
    files.download(ZIP_SALIDA)
except ImportError:
    print("\n(Fuera de Colab: el ZIP quedó en la carpeta de salida.)")
