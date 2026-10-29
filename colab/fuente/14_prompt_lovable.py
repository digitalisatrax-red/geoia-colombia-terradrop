#@title 14 · Generar el prompt de Lovable { display-mode: "form" }
def _lista_valores():
    return "\n".join(f"- **{t['titulo']}**: {t['valor_texto']}" + (f" — {t['detalle']}" if t.get("detalle") else "") for t in K["tarjetas"])

def _archivos():
    f = [f"- `kpis.json` → guárdalo en `public/data/kpis.json` (toda la información numérica y textual del tablero)."]
    desc = {"territorio": "límite del territorio de estudio", "municipio": "límite municipal (contexto)",
            "veredas": "veredas con sus indicadores (cod_ver, nom_ver, area_ha, pct_natural, bosque_ha, protegida_pct, vias_km, densidad_vias_km_km2, drenajes_km…)",
            "coberturas": "coberturas CLC 2024 por tipo (campos codigo, leyenda, n1, color, ha)",
            "areas_protegidas": "áreas protegidas RUNAP (nombre, categoria, ambito, naturaleza)", "vias": "vías (campo clase y clase_nombre)",
            "drenajes": "drenajes", "rios_principales": "ríos principales"}
    for n, i in ARCH_GEO.items():
        f.append(f"- `{i['archivo']}` → `public/data/{n}.geojson` · {desc.get(n, n)} ({i['elementos']} elementos, {i['kb']} kB).")
    f.append("- `mapa_ubicacion.png` → `public/img/mapa_ubicacion.png` (mapa de ubicación para la portada).")
    return "\n".join(f)

def prompt_completo():
    T_ = K["territorio"]
    tipo_txt = f"la vereda {T_['vereda']} del municipio de {T_['municipio']}" if T_["tipo"] == "vereda" else f"el municipio de {T_['municipio']}"
    veredas_txt = "Como el territorio es una vereda, la tabla se presenta como **ficha** (una sola fila) con los mismos indicadores." if ES_VEREDA else f"Hay {len(K['veredas'])} veredas en la tabla."
    return f"""# Prompt para Lovable · Tablero territorial «{T_['nombre']}»

Crea una aplicación web llamada **«Tablero territorial · {T_['nombre']}»** con React + Vite + TypeScript + Tailwind + shadcn/ui, gráficos con **Recharts** y mapa con **Leaflet (react-leaflet)**. Es un dashboard de **solo lectura**, 100 % estático (sin backend ni inicio de sesión), todo en **español de Colombia**, para sustentar el estudio territorial de {tipo_txt}, departamento de {T_['departamento']}. Los datos ya vienen procesados con SIG: **no inventes, no estimes y no recalcules ninguna cifra**.

## 1. Datos que voy a adjuntar
{_archivos()}

Reglas de datos:
- Toda cifra, etiqueta y texto analítico sale de `kpis.json` (carga con `fetch`). Las tarjetas están en `tarjetas`, los textos en `lecturas`, las fuentes en `fuentes`, las tablas en `cobertura`, `areas_protegidas`, `hidrografia`, `vias`, `cruces` y `veredas`.
- Si un bloque llega vacío o en `null`, muestra un estado vacío amable (p. ej. «No hay áreas protegidas del RUNAP que se traslapen con este territorio») en lugar de ocultar la sección.
- Formato colombiano: miles con punto y decimales con coma (1.234,5); áreas en **ha** y longitudes en **km**; porcentajes con un decimal.

## 2. Estructura de la página (una sola página, menú fijo con anclas y barra de progreso)
1. **Portada**: título grande, chips (departamento, municipio, vereda si aplica, área en ha, código DANE) y el `mapa_ubicacion.png` como imagen principal con botón «Descargar mapa». Debajo, «Lectura rápida» con las 3 primeras frases de `lecturas`.
2. **Resumen**: rejilla de tarjetas KPI con las tarjetas de los grupos `territorio`, `cobertura` y `areas_protegidas` (icono lucide, valor grande con animación de conteo, detalle pequeño).
3. **Territorio y cobertura**: dona con `cobertura.nivel1` (usa el campo `color`), barras horizontales con las 8 coberturas de nivel 3 más grandes, medidor de «cobertura natural y seminatural», bloque de fragmentación del bosque (parches, tamaño medio, parche mayor) y tooltip que explique el índice de Shannon en lenguaje sencillo.
4. **Áreas protegidas**: radial con `protegida_pct`, lista de `areas` (nombre, categoría, ámbito, ha en el territorio, % del territorio) con chips distintos para público/privado, y barras por categoría.
5. **Hidrografía**: tarjetas (km de drenajes, densidad km/km², ríos principales, cuerpos de agua CLC), barras con `drenajes_nombrados` y `rios_principales`, y un aviso discreto con `hidrografia.nota`.
6. **Vías y accesibilidad**: barras apiladas por clase de vía (km), dos semicírculos con el % del territorio a ≤ 1 km y ≤ 3 km de una vía, y ranking de `vias_nombradas`. Aviso con `vias.nota`.
7. **Cruces entre capas**: tarjetas con vías dentro de áreas protegidas, bosque protegido, drenajes en bosque y bosque cerca de vías, con la advertencia de `cruces.nota`.
8. **Mapa interactivo** (ver sección 4).
9. **Tabla por vereda**: buscador, columnas ordenables, barras de datos en `pct_natural`, `protegida_pct` y `densidad_vias_km_km2`, botón «Descargar CSV» y selector de indicador para colorear el mapa. Al pulsar una fila, el mapa hace zoom y resalta esa vereda. {veredas_txt}
10. **Lo que dicen los datos**: lista de `lecturas` como tarjetas cortas.
11. **Modo Aula** (pestaña o interruptor): 6 preguntas guía para discutir el territorio con estudiantes (cobertura dominante, qué tan transformado está, relación entre vías y bosque, qué protege el RUNAP aquí, qué vereda destaca y por qué, qué límites tienen los datos), cada una con un botón «ver pista» que lleve a la sección correspondiente.
12. **Fuentes y metodología** (pie de página): lista `fuentes`, el sistema de referencia ({CRS_METRICO}), la fecha de generación (`metadatos.generado`) y las limitaciones (escala 1:100.000 de CLC; capas de vías e hidrografía de Interés Colombia son de lectura territorial, no de ingeniería).

## 3. Valores de referencia (para que verifiques que el resultado coincide)
{_lista_valores()}

## 4. Mapa interactivo
- Base clara (CARTO Positron u OpenStreetMap), ajustado a los límites de `territorio.geojson`; contorno del territorio grueso y oscuro (#0d0d12).
- Capas con interruptores y leyenda plegable: coberturas (color del campo `color`), áreas protegidas (borde verde #0a7f55 con trama), drenajes (#2f9bff), ríos principales (#0b4fcf), vías (pavimentadas #e53935, sin pavimentar #ff7ab0, tiempo seco #b9763f en línea discontinua) y veredas (coropleta según el indicador elegido).
- Popups con los atributos de cada elemento (nombre, categoría, ha o km). Control de pantalla completa y botón «Volver al territorio».

## 5. Estilo visual «Clay»
- Fondo crema #f6f1e7, texto tinta #0d0d12, acentos naranja #ff9f1c, verde #27c98f, azul #2f9bff, rosa #ff7ab0 y morado #8b6cf0.
- Tarjetas tipo arcilla: radios de 28 px, sombra suave doble (luz arriba-izquierda, sombra abajo-derecha) y relieve sutil; botones redondeados con micro-animación al pasar el cursor.
- Tipografía geométrica redondeada (Sora o Nunito, de Google Fonts); títulos grandes y jerarquía clara.
- Diseño responsive (móvil primero), contraste AA, no depender solo del color (etiquetas e iconos), `aria-label` en gráficos y tablas con encabezados.

## 6. Fuentes bajo cada gráfico y tabla
Bajo **cada** gráfico, mapa o tabla añade una línea pequeña «Fuente: …» con el texto de `kpis.json → fuentes` que corresponda: `cobertura` (sección 3), `areas_protegidas` (4), `hidrografia` (5), `vias` (6), `limites` (tabla de veredas y mapa) y, en todos, `procesamiento`.

## 7. Criterios de aceptación
- Carga sin errores de consola y todas las cifras coinciden con la sección 3.
- Se ve bien en móvil y escritorio; el menú fijo resalta la sección activa.
- Las capas del mapa se activan y desactivan sin recargar; la tabla ordena y filtra.
- Ninguna sección muestra datos inventados: lo que no esté en los archivos aparece como estado vacío.
"""

def prompt_corto():
    T_ = K["territorio"]
    return f"""Crea un dashboard de solo lectura, en español de Colombia, llamado «Tablero territorial · {T_['nombre']}» ({T_['departamento']}) con React + Vite + TypeScript + Tailwind + shadcn/ui, Recharts y react-leaflet. Los datos ya están calculados: léelos de `public/data/kpis.json` y de los GeoJSON de `public/data/` (territorio, coberturas, areas_protegidas, vias, drenajes, rios_principales, veredas); no inventes ni recalcules cifras.

Secciones, en una sola página con menú fijo: 1) portada con `public/img/mapa_ubicacion.png` y chips (departamento, municipio, área en ha); 2) resumen con las tarjetas de `kpis.json → tarjetas`; 3) territorio y cobertura (dona nivel 1, barras nivel 3); 4) áreas protegidas; 5) hidrografía; 6) vías y accesibilidad (% del territorio a ≤ 1 y ≤ 3 km de una vía); 7) mapa interactivo con interruptores de capas; 8) tabla por vereda ordenable; 9) fuentes y metodología.

Estilo «Clay»: fondo crema #f6f1e7, tarjetas redondeadas con relieve suave, acentos naranja #ff9f1c, verde #27c98f y azul #2f9bff, tipografía redondeada. Formato colombiano de números (1.234,5), ha y km. Bajo cada gráfico y tabla pon una línea «Fuente: …» tomada de `kpis.json → fuentes`. Si un bloque viene vacío, muestra un estado vacío amable.

Haz primero esta estructura con datos reales; después te pediré el detalle de cada sección.
"""

with open(os.path.join(OUT, "prompt_lovable.md"), "w", encoding="utf-8") as f:
    f.write(prompt_completo())
with open(os.path.join(OUT, "prompt_lovable_corto.md"), "w", encoding="utf-8") as f:
    f.write(prompt_corto())
print(f"prompt_lovable.md ({len(prompt_completo())} caracteres) y prompt_lovable_corto.md ({len(prompt_corto())} caracteres) listos.\n")
print(prompt_corto())
