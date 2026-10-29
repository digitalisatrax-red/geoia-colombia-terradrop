#@title 2 · Parámetros { display-mode: "form" }
ORIGEN = "auto"            #@param ["auto", "zip", "api"]
RUTA_ZIP = ""              #@param {type:"string"}
CODIGO_MUNICIPIO = ""      #@param {type:"string"}
CODIGO_VEREDA = ""         #@param {type:"string"}
NOMBRE_PROYECTO = ""       #@param {type:"string"}
CARPETA_SALIDA = "salida_terradrop"  #@param {type:"string"}
DISTANCIAS_ACCESO_KM = [1, 3]        # franjas de accesibilidad alrededor de las vías

# Cómo se decide la fuente de datos cuando ORIGEN = "auto":
#   1) si RUTA_ZIP existe -> se usa ese ZIP;
#   2) si estás en Colab -> se te ofrece subir el ZIP de TerraDrop (puedes cancelar);
#   3) si hay CODIGO_MUNICIPIO -> se consultan las APIs oficiales.
