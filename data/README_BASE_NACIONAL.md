# Reto GeoIA Colombia — Base nacional inicial

Esta carpeta contiene la primera base nacional para construir el selector aleatorio y el flujo de análisis SIG.

## Archivos principales

- `municipios_selector.geojson`: municipios con atributos del selector.
- `municipios_selector.gpkg`: misma base en GeoPackage para QGIS.
- `municipios_selector_indice.csv`: índice ligero para el HTML y Colab.
- `runap_latest.zip`: descarga nacional del RUNAP.
- `rios_principales.geojson`: ríos principales.
- `humedales_atributos.json`: atributos nacionales de humedales MADS versión 3.
- `fuentes_base_nacional.json`: fuentes, fechas, URLs, estados y limitaciones.

## Regla de asignación inicial

El selector debe escoger solamente municipios cuyo campo `areas_protegidas` sea mayor que cero. En esta primera consulta se identificaron 801 municipios con al menos un área protegida intersectada por la capa RUNAP.

## Capas que se consultarán por municipio

Las vías, vías hasta tercer orden, drenajes sencillos, quebradas, cuerpos de agua, humedales y demás elementos de cartografía base se consultarán desde los servicios registrados en `fuentes_base_nacional.json` y se recortarán en Colab al municipio asignado.

## Advertencia de calidad

Los ríos principales no sustituyen la red completa de drenajes. La capa IGAC 1:25.000 tiene cobertura parcial según su descripción oficial. El sistema debe conservar esta advertencia en los metadatos y mostrarla en el dashboard.
