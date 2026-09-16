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

def listar_productos():
    productos = cargar_datos("productos")
    print("\n--- PRODUCTOS REGISTRADOS ---")
    filtro = input("Buscar por código o parte del nombre (vacío para todos): ").strip().upper()
    
    encontrados = False
    for p in productos:
        if filtro in p["codigo"] or filtro in p["nombre"].upper():
            estado = "Activo" if p["activo"] else "Inactivo"
            print(f"[{p['codigo']}] {p['nombre']} | Cat: {p['categoria']} | Precio: ${p['precio']} | Stock Min: {p['stock_minimo']} | Estado: {estado}")
            encontrados = True
    
    if not encontrados:
        print("No se encontraron productos.")

def desactivar_producto():
    codigo = input("Código del producto a desactivar: ").strip().upper()
    productos = cargar_datos("productos")
    for p in productos:
        if p["codigo"] == codigo:
            p["activo"] = False
            guardar_datos("productos", productos)
            print(f"Producto {codigo} desactivado exitosamente (conserva su historial).")
            return
    print("Producto no encontrado.")

def registrar_lote():
    print("\n--- REGISTRAR LOTE PRODUCTIVO ---")
    id_lote = input("ID de lote (ej. L001): ").strip().upper()
    lotes = cargar_datos("lotes")
    if any(l["id_lote"] == id_lote for l in lotes):
        print("Error: El ID del lote ya existe.")
        return

    prod_codigo = input("Código del producto asociado: ").strip().upper()
    productos = cargar_datos("productos")
    producto = next((p for p in productos if p["codigo"] == prod_codigo and p["activo"]), None)
    
    if not producto:
        print("Error: El producto no existe o está inactivo.")
        return

    fecha_siembra = input("Fecha de siembra (AAAA-MM-DD): ").strip()
    try:
        area_m2 = float(input("Área en m2: "))
    except ValueError:
        print("Error: El área debe ser un valor numérico.")
        return

    nuevo_lote = {
        "id_lote": id_lote,
        "producto_codigo": prod_codigo,
        "fecha_siembra": fecha_siembra,
        "area_m2": area_m2,
        "cantidad_producida": 0,
        "estado": "EN_PRODUCCION"
    }
    lotes.append(nuevo_lote)
    guardar_datos("lotes", lotes)
    print(f"Lote {id_lote} registrado en estado EN_PRODUCCION.")

def cosechar_lote():
    print("\n--- COSECHAR LOTE ---")
    id_lote = input("ID del lote a cosechar: ").strip().upper()
    lotes = cargar_datos("lotes")
    lote = next((l for l in lotes if l["id_lote"] == id_lote), None)

    if not lote:
        print("Error (PF003): El lote no existe.")
        return
    if lote["estado"] != "EN_PRODUCCION":
        print("Error (PF004): El lote ya fue cosechado o cancelado.")
        return

    try:
        cantidad = float(input("Cantidad producida cosechada: "))
        if cantidad <= 0:
            print("Error: La cantidad debe ser mayor a 0.")
            return
    except ValueError:
        print("Error: Ingrese un valor numérico.")
        return

    lote["cantidad_producida"] = cantidad
    lote["estado"] = "COSECHADO"
    guardar_datos("lotes", lotes)

    movimientos = cargar_datos("movimientos")
    id_mov = f"M{len(movimientos)+1:04d}"
    nuevo_mov = {
        "id": id_mov,
        "producto_codigo": lote["producto_codigo"],
        "tipo": "ENTRADA",
        "cantidad": cantidad,
        "motivo": f"Cosecha lote {id_lote}",
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    movimientos.append(nuevo_mov)
    guardar_datos("movimientos", movimientos)
    print(f"Lote {id_lote} cosechado. Entrada de inventario {id_mov} generada.")
    