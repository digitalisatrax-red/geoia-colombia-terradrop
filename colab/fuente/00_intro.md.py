# [markdown]
# # 🌎 GeoIA Colombia · TerraDrop → KPI → Prompt para Lovable
#
# Este cuaderno toma las **capas que descarga TerraDrop** (o las consulta en vivo a los servicios oficiales) para un **municipio o una vereda**, calcula **KPI e indicadores** y termina entregándote:
#
# | Archivo | Para qué sirve |
# |---|---|
# | `prompt_lovable.md` | El prompt completo (en español) para crear el dashboard en [Lovable](https://lovable.dev) |
# | `prompt_lovable_corto.md` | Versión corta para el primer mensaje; luego iteras con el completo |
# | `kpis.json` | Todos los indicadores, listos para alimentar el dashboard |
# | `geojson/*.geojson` | Territorio y capas **livianas** (simplificadas) para el mapa interactivo |
# | `tablas/*.csv` | Tablas de cobertura, áreas protegidas, hidrografía, vías y veredas |
# | `mapa_ubicacion.png` | Mapa de ubicación (Colombia → departamento → territorio con capas) |
#
# **Grupos de KPI:** 1) Territorio y cobertura · 2) Áreas protegidas · 3) Hidrografía · 4) Vías y accesibilidad (+ cruces entre capas y tabla por vereda).
#
# ### Cómo usarlo
# 1. Ejecuta las celdas en orden (**Entorno → Entorno de ejecución → Ejecutar todo**).
# 2. En la celda *Parámetros* elige el origen:
#    * **auto** (recomendado): usa el ZIP de TerraDrop si lo subes; si no, consulta las APIs con el código DANE.
#    * **zip**: solo el ZIP que descargaste en TerraDrop (`terradrop_<código>_<municipio>.zip`).
#    * **api**: consulta en vivo con `CODIGO_MUNICIPIO` (5 dígitos) y, si quieres una vereda, `CODIGO_VEREDA` (8 dígitos).
# 3. Al final se descarga `paquete_lovable_….zip`. Sube su contenido a Lovable junto con `prompt_lovable.md`.
#
# > Las áreas y longitudes se calculan en **MAGNA-SIRGAS Origen Nacional (EPSG:9377)**. Los datos son los de cada fuente oficial; revisa su vigencia en la página *Fuentes y calidad* de TerraDrop.
