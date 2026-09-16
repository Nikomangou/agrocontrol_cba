import json
import os
from datetime import datetime

DATA_DIR = "data"
ARCHIVOS = {
    "productos": os.path.join(DATA_DIR, "productos.json"),
    "lotes": os.path.join(DATA_DIR, "lotes.json"),
    "movimientos": os.path.join(DATA_DIR, "movimientos.json"),
    "ventas": os.path.join(DATA_DIR, "ventas.json")
}

def inicializar_almacenamiento():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    for ruta in ARCHIVOS.values():
        if not os.path.exists(ruta):
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=4)

def cargar_datos(llave):
    inicializar_almacenamiento()
    try:
        with open(ARCHIVOS[llave], "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def guardar_datos(llave, datos):
    with open(ARCHIVOS[llave], "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)
        