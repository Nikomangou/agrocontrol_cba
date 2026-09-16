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

def registrar_producto():
    print("\n--- REGISTRAR PRODUCTO ---")
    codigo = input("Código del producto: ").strip().upper()
    if not codigo:
        print("Error: El código no puede estar vacío.")
        return
    
    productos = cargar_datos("productos")
    if any(p["codigo"] == codigo for p in productos):
        print("Error (PF001): Ya existe un producto registrado con ese código.")
        return
    
    nombre = input("Nombre: ").strip()
    categoria = input("Categoría: ").strip()
    unidad = input("Unidad de medida (ej. kilo, unidad): ").strip()
    
    try:
        precio = float(input("Precio ($): "))
        stock_minimo = int(input("Stock mínimo: "))
        if precio <= 0 or stock_minimo < 0:
            print("Error (PF002): El precio debe ser mayor a 0 y el stock mínimo >= 0.")
            return
    except ValueError:
        print("Error (PF002): Ingrese valores numéricos válidos.")
        return

    nuevo_producto = {
        "codigo": codigo,
        "nombre": nombre,
        "categoria": categoria,
        "unidad": unidad,
        "precio": precio,
        "stock_minimo": stock_minimo,
        "activo": True
    }
    productos.append(nuevo_producto)
    guardar_datos("productos", productos)
    print(f"Producto '{nombre}' registrado con éxito.")
