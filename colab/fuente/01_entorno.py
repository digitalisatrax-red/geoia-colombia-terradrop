#@title 1 · Preparar el entorno { display-mode: "form" }
import importlib, subprocess, sys

def _asegurar(paquete, modulo):
    try:
        importlib.import_module(modulo)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", paquete])

for _p, _m in [("geopandas", "geopandas"), ("pyogrio", "pyogrio"), ("shapely>=2.0", "shapely"),
               ("pyproj", "pyproj"), ("matplotlib", "matplotlib"), ("requests", "requests")]:
    _asegurar(_p, _m)

import os, re, io, json, math, time, zipfile, shutil, datetime, warnings, unicodedata
import numpy as np
import pandas as pd
import geopandas as gpd
import requests
import shapely
from shapely.geometry import box, Point
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

warnings.filterwarnings("ignore")
print("Listo · geopandas", gpd.__version__, "· shapely", shapely.__version__)
