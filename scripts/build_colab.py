#!/usr/bin/env python3
"""Arma colab/terradrop_kpis_lovable.ipynb a partir de colab/fuente/NN_*.py (una celda por archivo).
Las celdas Markdown empiezan con la línea '# [markdown]' y sus líneas van comentadas con '# '.
Uso: python3 scripts/build_colab.py"""
import json, glob, os, uuid
raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
celdas = []
for ruta in sorted(glob.glob(os.path.join(raiz, "colab", "fuente", "[0-9][0-9]_*.py"))):
    lineas = open(ruta, encoding="utf-8").read().rstrip("\n").split("\n")
    if lineas[0].strip() == "# [markdown]":
        texto = "\n".join(l[2:] if l.startswith("# ") else l[1:] if l.startswith("#") else l for l in lineas[1:])
        celdas.append({"cell_type": "markdown", "id": uuid.uuid4().hex[:8], "metadata": {}, "source": texto.splitlines(True)})
    else:
        celdas.append({"cell_type": "code", "id": uuid.uuid4().hex[:8], "metadata": {"cellView": "form"} if lineas[0].startswith("#@title") else {},
                       "execution_count": None, "outputs": [], "source": ("\n".join(lineas)).splitlines(True)})
nb = {"cells": celdas, "metadata": {"colab": {"provenance": [], "name": "terradrop_kpis_lovable.ipynb"},
      "kernelspec": {"name": "python3", "display_name": "Python 3"}, "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 5}
destino = os.path.join(raiz, "colab", "terradrop_kpis_lovable.ipynb")
json.dump(nb, open(destino, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("OK", destino, len(celdas), "celdas")
