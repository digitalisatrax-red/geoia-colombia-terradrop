# Colab · KPI e indicadores → prompt de Lovable

Cuaderno: [`terradrop_kpis_lovable.ipynb`](https://colab.research.google.com/github/digitalisatrax-red/geoia-colombia-terradrop/blob/main/colab/terradrop_kpis_lovable.ipynb) (abrir en Colab).

## Qué hace
1. **Carga** las capas: el ZIP de TerraDrop (`terradrop_<código>_<municipio>.zip`) o, si no lo subes, las consulta a los servicios oficiales con `CODIGO_MUNICIPIO` (5 dígitos) y opcionalmente `CODIGO_VEREDA` (8 dígitos).
2. **Prepara** el territorio (municipio o vereda): repara geometrías, proyecta a MAGNA-SIRGAS Origen Nacional (EPSG:9377) y recorta todas las capas.
3. **Calcula KPI** en cuatro familias (más cruces entre capas y una tabla por vereda):
   * *Territorio y cobertura*: área, perímetro, peso de la vereda en el municipio, coberturas CLC 2024 (niveles 1–3), % natural/seminatural, bosque y fragmentación, diversidad de Shannon.
   * *Áreas protegidas*: áreas RUNAP traslapadas, hectáreas y % protegido, por categoría, ámbito y naturaleza (pública/privada).
   * *Hidrografía*: km de drenajes, densidad km/km², drenajes y ríos principales con nombre, cuerpos de agua (CLC).
   * *Vías y accesibilidad*: km por clase, % pavimentadas, densidad, % del territorio a ≤ 1 y ≤ 3 km de una vía.
   * *Cruces*: vías en áreas protegidas, bosque protegido, drenajes en bosque, bosque cerca de vías.
4. **Exporta** `kpis.json`, `tablas/*.csv`, `geojson/*.geojson` livianos y `mapa_ubicacion.png`.
5. **Genera** `prompt_lovable.md` (completo) y `prompt_lovable_corto.md` (primer mensaje), con los valores de referencia y notas «Fuente» para cada gráfico y tabla, y empaqueta todo en `paquete_lovable_….zip`.

## Cómo usarlo en Lovable
1. Pega `prompt_lovable_corto.md` en un proyecto nuevo y arrastra `kpis.json`, la carpeta `geojson/` y `mapa_ubicacion.png`.
2. Con la estructura lista, pega `prompt_lovable.md` para afinar cada sección.
3. Verifica que las cifras coincidan con la sección *Valores de referencia* del prompt.

## Mantenimiento
El cuaderno se genera desde `colab/fuente/NN_*.py` (una celda por archivo). Tras editar esos archivos ejecuta `python3 scripts/build_colab.py`.

## Límites que conviene decir en clase
* CLC 2024 está a escala 1:100.000; las vías e hidrografía de Interés Colombia sirven para lectura territorial, no para ingeniería.
* Las capas descargadas intersectan el territorio; el cuaderno las **recorta** antes de medir.
* Las áreas se calculan en EPSG:9377; pueden diferir en décimas de punto porcentual de las áreas oficiales de DANE.
