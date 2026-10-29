#@title 13 · Mapa de ubicación (PNG) { display-mode: "form" }
from matplotlib import pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle

FONDO, TINTA, NARANJA, PAPEL = "#f6f1e7", "#0d0d12", "#ff9f1c", "#fffaf0"

def contexto_departamentos():
    """Departamentos simplificados para los recuadros de ubicación. Si no hay red, devuelve (None, None)."""
    try:
        todos = consultar("dep", url=URL_DEPARTAMENTOS, page=100, spatial=False,
                          extra={"maxAllowableOffset": 0.02, "geometryPrecision": 3})
        if len(todos) == 0:
            return None, None
        cc = col(todos, "cod_dane")
        clave = todos[cc].astype(str).str.replace(r"\.0$", "", regex=True).map(lambda s: s.lstrip("0") or "0")
        mio = todos[clave == str(int(COD_MUN[:2]))]
        det = None
        if len(mio):
            valor = mio[cc].iloc[0]
            cond = f"{cc}={valor}" if isinstance(valor, (int, float, np.integer)) else f"{cc}='{valor}'"
            det = consultar("dep", where=cond, url=URL_DEPARTAMENTOS, page=100, spatial=False,
                            extra={"maxAllowableOffset": 0.004, "geometryPrecision": 4})
            det = det if len(det) else mio
        return todos.assign(_clave=clave).to_crs(CRS_METRICO), (det.to_crs(CRS_METRICO) if det is not None else None)
    except Exception as e:
        print("  (sin contexto departamental:", str(e)[:80], ")")
        return None, None

def barra_escala(ax):
    xa, xb = ax.get_xlim(); ya, yb = ax.get_ylim()
    ancho = xb - xa
    opciones = [50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000]
    L_ = max([o for o in opciones if o <= ancho / 3.5] or [opciones[0]])
    x_ini, y_ini, alto = xa + ancho * 0.04, ya + (yb - ya) * 0.045, (yb - ya) * 0.012
    for i in range(4):
        ax.add_patch(Rectangle((x_ini + i * L_ / 4, y_ini), L_ / 4, alto, fc=TINTA if i % 2 == 0 else "white", ec=TINTA, lw=.8, zorder=30))
    et = f"{L_/1000:g} km" if L_ >= 1000 else f"{L_} m"
    caja = dict(boxstyle="round,pad=.15", fc=PAPEL, ec="none", alpha=.9)
    ax.text(x_ini, y_ini + alto * 2.2, "0", fontsize=8, va="bottom", ha="center", zorder=30, bbox=caja)
    ax.text(x_ini + L_, y_ini + alto * 2.2, et, fontsize=8, va="bottom", ha="center", zorder=30, bbox=caja)

def mapa_ubicacion(ruta_png):
    deps, dep_sel = contexto_departamentos()
    fig = plt.figure(figsize=(16, 9), dpi=150, facecolor=FONDO)
    gs = GridSpec(2, 2, width_ratios=[0.33, 0.67], height_ratios=[1, 1], left=.03, right=.985, top=.855, bottom=.115, wspace=.035, hspace=.14)
    ax_c, ax_d, ax = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[:, 1])
    for a in (ax_c, ax_d, ax):
        a.set_facecolor(PAPEL); a.set_xticks([]); a.set_yticks([]); a.set_xlabel(""); a.set_ylabel("")
        for s in a.spines.values():
            s.set_color(TINTA); s.set_linewidth(1.2)
    pt = gpd.GeoSeries([TERR_GEOM.centroid], crs=CRS_METRICO)

    # --- Colombia ---
    ax_c.set_title("Colombia", fontsize=12, fontweight="bold", color=TINTA, loc="left")
    if deps is not None:
        deps.plot(ax=ax_c, color="#ddd5c3", edgecolor="white", linewidth=.5)
        sel = deps[deps["_clave"] == str(int(COD_MUN[:2]))]
        if len(sel):
            sel.plot(ax=ax_c, color=NARANJA, edgecolor=TINTA, linewidth=.8)
        pt.plot(ax=ax_c, color="#d92d20", markersize=26, edgecolor="white", linewidth=.8, zorder=5)
        ax_c.set_aspect("equal", adjustable="datalim")
    else:
        ax_c.text(.5, .5, "Contexto nacional\nno disponible\n(sin conexión)", ha="center", va="center", fontsize=10, color="#666", transform=ax_c.transAxes)

    # --- Departamento ---
    ax_d.set_title(f"Departamento de {NOM_DPTO}" if NOM_DPTO else "Departamento", fontsize=12, fontweight="bold", color=TINTA, loc="left")
    if dep_sel is not None and len(dep_sel):
        dep_sel.plot(ax=ax_d, color="#efe8d6", edgecolor=TINTA, linewidth=1)
        mun.plot(ax=ax_d, color=NARANJA, edgecolor=TINTA, linewidth=.8, alpha=.9 if not ES_VEREDA else .55)
        if ES_VEREDA:
            TERR.plot(ax=ax_d, color="#d92d20", edgecolor="#d92d20", linewidth=1.2)
        ax_d.set_aspect("equal", adjustable="datalim")
    else:
        mun.plot(ax=ax_d, color=NARANJA, edgecolor=TINTA, linewidth=.8)
        ax_d.set_aspect("equal", adjustable="datalim")
    mb = MUN_GEOM.centroid
    ax_d.annotate(NOM_MUN, (mb.x, mb.y), xytext=(0, 14), textcoords="offset points", ha="center", fontsize=9, fontweight="bold",
                  color=TINTA, bbox=dict(boxstyle="round,pad=.2", fc="white", ec=TINTA, lw=.6), zorder=9)

    # --- Territorio con capas ---
    ax.set_title("Territorio de estudio y capas de análisis", fontsize=12, fontweight="bold", color=TINTA, loc="left")
    if ES_VEREDA:
        mun.plot(ax=ax, color="#ece5d4", edgecolor="#9b927e", linewidth=.8, zorder=1)
    if CLC_OK and len(clc):
        clc.plot(ax=ax, color=clc["n1"].map(CLC_COL).fillna("#cccccc").tolist(), edgecolor="none", alpha=.82, zorder=2)
    else:
        TERR.plot(ax=ax, color="#ece5d4", edgecolor="none", zorder=2)
    if len(VER_M) > 1:
        VER_M.boundary.plot(ax=ax, color="#ffffff", linewidth=.5, alpha=.8, zorder=3)
    if AP_GEOM is not None:
        ap.plot(ax=ax, facecolor="none", edgecolor="#0a7f55", hatch="///", linewidth=1.4, zorder=4)
    if len(D["drenajes"]):
        D["drenajes"].plot(ax=ax, color="#2f9bff", linewidth=.6, zorder=5)
    if len(D["rios_principales"]):
        D["rios_principales"].plot(ax=ax, color="#0b4fcf", linewidth=1.8, zorder=6)
    for cid, color, lw, ls in (("vias_tiempo_seco", "#b9763f", 1.0, (0, (4, 2))), ("vias_sin_pavimentar", "#ff7ab0", 1.3, "-"), ("vias_pavimentadas", "#e53935", 2.0, "-")):
        if len(D[cid]):
            D[cid].plot(ax=ax, color=color, linewidth=lw, linestyle=ls, zorder=7)
    TERR.boundary.plot(ax=ax, color=TINTA, linewidth=2.6, zorder=10)
    mx, my = (x1 - x0) * .06, (y1 - y0) * .06
    ax.set_xlim(x0 - mx, x1 + mx); ax.set_ylim(y0 - my, y1 + my); ax.set_aspect("equal", adjustable="datalim")
    ax.apply_aspect()
    barra_escala(ax)
    ax.annotate("N", xy=(.955, .95), xytext=(.955, .83), xycoords="axes fraction", ha="center", fontsize=15, fontweight="bold", color=TINTA,
                arrowprops=dict(arrowstyle="-|>", color=TINTA, lw=2.2), zorder=40)

    for a in (ax_c, ax_d, ax):
        a.set_xlabel(""); a.set_ylabel("")
    # --- leyenda en una franja inferior ---
    items = [Patch(fc=CLC_COL[k], ec="none", alpha=.82, label=CLC_N1[k]) for k in CLC_N1] if CLC_OK else []
    items += [Patch(fc="none", ec="#0a7f55", hatch="///", label="Áreas protegidas (RUNAP)"),
              Line2D([], [], color="#2f9bff", lw=1, label="Drenajes"), Line2D([], [], color="#0b4fcf", lw=2.2, label="Ríos principales"),
              Line2D([], [], color="#e53935", lw=2.4, label="Vías pavimentadas"), Line2D([], [], color="#ff7ab0", lw=1.6, label="Vías sin pavimentar"),
              Line2D([], [], color="#b9763f", lw=1.2, ls=(0, (4, 2)), label="Vías en tiempo seco"), Line2D([], [], color=TINTA, lw=2.6, label="Límite del territorio")]
    fig.legend(handles=items, loc="lower center", ncol=6, fontsize=8.6, frameon=True, facecolor=PAPEL, edgecolor=TINTA, bbox_to_anchor=(.5, .028), columnspacing=1.2, handlelength=1.8)

    fig.text(.03, .945, f"Mapa de ubicación · {NOM_TERR_TITULO}", fontsize=24, fontweight="bold", color=TINTA, va="center")
    sub = f"{NOM_DPTO}, Colombia  ·  {fmt(AREA_T_HA, 1)} ha  ·  código DANE {COD_VER or COD_MUN}"
    fig.text(.03, .897, sub, fontsize=12.5, color="#4a4a55", va="center")
    fig.text(.03, .012, f"Fuentes: DANE (límites), IDEAM (Corine Land Cover 2024), MinAmbiente (RUNAP), IGAC (vías e hidrografía). Sistema de referencia: MAGNA-SIRGAS Origen Nacional ({CRS_METRICO}). "
             f"Elaboración propia con GeoIA Colombia · TerraDrop, {fecha}.", fontsize=7.6, color="#555", va="center")
    fig.savefig(ruta_png, dpi=150, facecolor=FONDO)
    plt.show()
    plt.close(fig)

RUTA_MAPA = os.path.join(OUT, "mapa_ubicacion.png")
mapa_ubicacion(RUTA_MAPA)
print("Mapa guardado:", RUTA_MAPA)
