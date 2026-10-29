# GeoIA Colombia · TerraDrop

**Gestor de descarga de datos territoriales para aprender, enseñar y trabajar con geovisores.**
Sitio estático (HTML + CSS + JavaScript, sin compilar) pensado para publicarse en GitHub Pages.

## Qué incluye

| Página | Archivo | Qué hace |
|---|---|---|
| Inicio | `index.html` | Presentación, capas por grupo con mapas, cuadro de petición al asistente. |
| TerraDrop | `descargas.html` | Selector departamento → municipio → vereda, buscador de municipios y de veredas por nombre (todo el país), **Modo Aula** con sorteo reproducible de municipio o de vereda, cola de descarga y ZIP. |
| Aula Geovisor | `aula.html` | Lección: por qué el geovisor es el núcleo de la información, comparación tabla vs. mapa, cuatro geovisores, anatomía de un visor, cuestionario. |
| Colombia en Mapas, clic a clic | `colombia-en-mapas.html` | Réplica didáctica del visor del IGAC con recorrido guiado de 24 pasos. |
| Fuentes | `fuentes.html` | Servicios consultados, fecha de verificación y advertencias de calidad. |

## Del dato al dashboard: Colab de KPI → Lovable

`colab/terradrop_kpis_lovable.ipynb` toma el ZIP de TerraDrop (o consulta las APIs con el código DANE), calcula KPI de territorio y cobertura, áreas protegidas, hidrografía y vías/accesibilidad, y entrega `kpis.json`, GeoJSON livianos, tablas CSV, el mapa de ubicación y el prompt para crear el dashboard en Lovable. Ábrelo en Colab: [abrir](https://colab.research.google.com/github/digitalisatrax-red/geoia-colombia-terradrop/blob/main/colab/terradrop_kpis_lovable.ipynb). Detalles en `colab/README.md`.

## Cómo funciona la descarga

El navegador consulta **directamente** los servicios ArcGIS REST de las entidades (IDEAM, IGAC, Ministerio de Ambiente) filtrando por el polígono del territorio elegido, y empaqueta un ZIP con GeoJSON por capa, un `LEEME.txt` y `asignacion_CODIGO.geojson`. No hay servidor propio ni se almacenan datos.

Capas: límite municipal, veredas DANE 2024, áreas protegidas (RUNAP vía MinAmbiente), vías (pavimentadas, sin pavimentar, tiempo seco), ríos principales, drenajes y coberturas CLC 2024.

El asistente del cuadro de texto es un **intérprete por reglas local** (no un modelo de lenguaje): entiende frases como «vías y drenajes de Jardín, Antioquia».

## Ejecutar en local

Opción 1, sin instalar nada: doble clic en `index.html` (los datos de `data/` se leen de las copias `.js`).

Opción 2, con servidor:

```bash
python -m http.server 8000
# abrir http://localhost:8000
```

Para las descargas hace falta conexión a internet: se piden en vivo a los servicios oficiales.

## Publicar en GitHub Pages

1. Crea el repositorio y sube todo el contenido de esta carpeta (incluye `.nojekyll`).
2. En *Settings → Pages* elige *Deploy from a branch*, rama `main`, carpeta `/ (root)`.
3. Abre la URL que GitHub te muestre. Las descargas funcionan en cualquier navegador con internet, pero **no dentro de una vista previa incrustada** que bloquee conexiones externas.

## Estructura

```
index.html · descargas.html · aula.html · colombia-en-mapas.html · fuentes.html
assets/css/site.css            sistema de diseño
assets/js/                     common, home, layers (servicios), descargas, aula, tour
assets/img/                    ilustraciones SVG estilo 3D juguetón
data/municipios.json           índice compacto de 1.121 municipios (801 con áreas protegidas)
data/mapa_colombia.json        siluetas departamentales y municipales para los mapas
data/fuentes_base_nacional.json  fuentes, fechas y limitaciones
data/*.js                      copias de los JSON para abrir con doble clic (scripts/make_data_js.py)
scripts/make_art.py            genera las ilustraciones
scripts/build_map.py           genera data/mapa_colombia.json desde las partes GeoJSON del IDEAM
scripts/make_data_js.py        regenera data/*.js tras cambiar un JSON
scripts/build_colab.py         arma colab/terradrop_kpis_lovable.ipynb desde colab/fuente/*.py
colab/                         cuaderno de KPI → prompt de Lovable (+ fuente por celdas)
```

## Datos que NO están en el repositorio

La carpeta de trabajo contiene archivos pesados que no se incluyen (CLC ≈ 1,2 GB, veredas ≈ 85 MB en 161 partes, ríos principales ≈ 53 MB, `runap_latest.zip` ≈ 70 MB). El sitio no los necesita porque descarga en vivo. Si quieres versionarlos, usa Git LFS o *Releases*.
También se excluyó a propósito material de clientes e instituciones que no pertenece al proyecto.

## Notas de calidad

- Los límites del mapa salen de la capa municipal del IDEAM con simplificación topológica (≈400 m); el municipio elegido se redibuja en vivo desde la API.
- Las capas **intersectan** el territorio, no lo recortan (usa *Cortar* en QGIS).
- «Ríos principales» no es la red completa de drenajes.
- El índice local tiene 1.121 municipios; el IDEAM publica 1.122 registros.
- Los servicios públicos pueden cambiar o caerse; verificados el 28-oct-2026 (ver `fuentes.html`).
- La réplica de Colombia en Mapas es didáctica y no oficial.

## Licencia

Código bajo MIT (ver `LICENSE`). Los datos descargados pertenecen a sus entidades productoras (IDEAM, IGAC, MinAmbiente, DANE, Parques Nacionales); cita siempre la fuente original.
