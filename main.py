import csv
import json
import os
import shutil
from datetime import datetime

DATA_DIR = "data"
BACKUP_DIR = os.path.join(DATA_DIR, "backups")
ARCHIVOS = {
    "productos": os.path.join(DATA_DIR, "productos.json"),
    "lotes": os.path.join(DATA_DIR, "lotes.json"),
    "movimientos": os.path.join(DATA_DIR, "movimientos.json"),
    "ventas": os.path.join(DATA_DIR, "ventas.json"),
    "usuarios": os.path.join(DATA_DIR, "usuarios.json")
}

USUARIO_ACTUAL = None

def inicializar_almacenamiento():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        
    for ruta in ARCHIVOS.values():
        if not os.path.exists(ruta):
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=4)

    try:
        with open(ARCHIVOS["usuarios"], "r", encoding="utf-8") as f:
            usuarios = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        usuarios = []

    if not usuarios:
        default_users = [
            {"usuario": "admin", "clave": "admin123", "rol": "ADMINISTRADOR"},
            {"usuario": "operador", "clave": "operador123", "rol": "OPERADOR"}
        ]
        guardar_datos("usuarios", default_users, realizar_backup=False)

def crear_copia_seguridad():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    for llave, ruta in ARCHIVOS.items():
        if os.path.exists(ruta) and llave != "usuarios":
            nombre_archivo = os.path.basename(ruta)
            respaldo_path = os.path.join(BACKUP_DIR, f"{timestamp}_{nombre_archivo}")
            shutil.copy(ruta, respaldo_path)

def cargar_datos(llave):
    try:
        with open(ARCHIVOS[llave], "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def guardar_datos(llave, datos, realizar_backup=True):
    if realizar_backup and llave != "usuarios":
        crear_copia_seguridad()
    with open(ARCHIVOS[llave], "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

def iniciar_sesion():
    global USUARIO_ACTUAL
    print("\n==================== INICIO DE SESIÓN ====================")
    usuarios = cargar_datos("usuarios")
    intentos = 0
    while intentos < 3:
        usr = input("Usuario: ").strip()
        pwd = input("Contraseña: ").strip()
        user_match = next((u for u in usuarios if u["usuario"] == usr and u["clave"] == pwd), None)
        if user_match:
            USUARIO_ACTUAL = user_match
            print(f"✓ Sesión iniciada como '{usr}' | Rol: [{USUARIO_ACTUAL['rol']}]")
            return True
        else:
            intentos += 1
            print(f"Credenciales incorrectas. Intentos restantes: {3 - intentos}")
    return False

def verificar_permisos(roles_permitidos):
    if USUARIO_ACTUAL and USUARIO_ACTUAL["rol"] in roles_permitidos:
        return True
    print(f"Error de acceso: Esta función requiere rol {', '.join(roles_permitidos)}.")
    return False

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
        costo = float(input("Costo unitario ($): "))
        precio = float(input("Precio de venta ($): "))
        stock_minimo = int(input("Stock mínimo: "))
        if costo <= 0 or precio <= 0 or stock_minimo < 0:
            print("Error (PF002): El costo y precio deben ser mayores a 0 y el stock mínimo >= 0.")
            return
    except ValueError:
        print("Error (PF002): Ingrese valores numéricos válidos.")
        return

    nuevo_producto = {
        "codigo": codigo,
        "nombre": nombre,
        "categoria": categoria,
        "unidad": unidad,
        "costo": costo,
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
            costo = p.get("costo", 0.0)
            print(f"[{p['codigo']}] {p['nombre']} | Cat: {p['categoria']} | Costo: ${costo:,.2f} | Precio: ${p['precio']:,.2f} | Stock Min: {p['stock_minimo']} | Estado: {estado}")
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

    fecha_siembra = input("Fecha de siembra (AAAA-MM-DD): ").strip() or datetime.now().strftime("%Y-%m-%d")
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

def calcular_stock(codigo_producto):
    movimientos = cargar_datos("movimientos")
    stock = 0
    for m in movimientos:
        if m["producto_codigo"] == codigo_producto:
            if m["tipo"] == "ENTRADA":
                stock += m["cantidad"]
            elif m["tipo"] == "SALIDA":
                stock -= m["cantidad"]
    return stock

def registrar_movimiento_manual():
    print("\n--- MOVIMIENTO MANUAL DE INVENTARIO ---")
    codigo = input("Código del producto: ").strip().upper()
    productos = cargar_datos("productos")
    if not any(p["codigo"] == codigo for p in productos):
        print("Error: Producto no existe.")
        return

    tipo = input("Tipo (ENTRADA/SALIDA): ").strip().upper()
    if tipo not in ["ENTRADA", "SALIDA"]:
        print("Tipo de movimiento inválido.")
        return

    try:
        cantidad = float(input("Cantidad: "))
        if cantidad <= 0:
            print("La cantidad debe ser mayor a 0.")
            return
    except ValueError:
        print("Cantidad inválida.")
        return

    if tipo == "SALIDA":
        stock_actual = calcular_stock(codigo)
        if cantidad > stock_actual:
            print(f"Error (PF005): Stock insuficiente. Stock actual: {stock_actual}")
            return

    motivo = input("Motivo (obligatorio): ").strip()
    if not motivo:
        print("El motivo es obligatorio.")
        return

    movimientos = cargar_datos("movimientos")
    id_mov = f"M{len(movimientos)+1:04d}"
    movimientos.append({
        "id": id_mov,
        "producto_codigo": codigo,
        "tipo": tipo,
        "cantidad": cantidad,
        "motivo": motivo,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    guardar_datos("movimientos", movimientos)
    print(f"Movimiento {id_mov} registrado correctamente.")

def registrar_venta():
    print("\n--- REGISTRAR VENTA ---")
    productos = cargar_datos("productos")
    items_venta = []
    
    while True:
        codigo = input("Código de producto a vender (o 'FIN' para terminar): ").strip().upper()
        if codigo == "FIN":
            break
        
        prod = next((p for p in productos if p["codigo"] == codigo and p["activo"]), None)
        if not prod:
            print("Producto no encontrado o inactivo.")
            continue
        
        stock_disp = calcular_stock(codigo)
        print(f"Producto: {prod['nombre']} | Precio: ${prod['precio']} | Stock Disponible: {stock_disp}")
        
        try:
            cant = int(input("Cantidad a vender: "))
            if cant <= 0:
                print("La cantidad debe ser mayor a 0.")
                continue
            cant_acumulada = sum(item["cantidad"] for item in items_venta if item["codigo"] == codigo)
            if (cant + cant_acumulada) > stock_disp:
                print("Error: No hay suficiente stock para cubrir esta cantidad.")
                continue
        except ValueError:
            print("Cantidad inválida.")
            continue

        items_venta.append({
            "codigo": codigo,
            "cantidad": cant,
            "costo_unitario": prod.get("costo", 0.0),
            "precio_unitario": prod["precio"]
        })

    if not items_venta:
        print("Venta cancelada. No se agregaron productos.")
        return

    ventas = cargar_datos("ventas")
    id_venta = f"V{len(ventas)+1:04d}"
    total_venta = sum(item["cantidad"] * item["precio_unitario"] for item in items_venta)
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")

    movimientos = cargar_datos("movimientos")
    for item in items_venta:
        id_mov = f"M{len(movimientos)+1:04d}"
        movimientos.append({
            "id": id_mov,
            "producto_codigo": item["codigo"],
            "tipo": "SALIDA",
            "cantidad": item["cantidad"],
            "motivo": f"Venta {id_venta}",
            "fecha": fecha_actual
        })

    ventas.append({
        "id": id_venta,
        "fecha": fecha_actual,
        "estado": "COMPLETADA",
        "items": items_venta,
        "total": total_venta
    })

    guardar_datos("movimientos", movimientos)
    guardar_datos("ventas", ventas)
    print(f"Venta {id_venta} registrada con éxito. Total: ${total_venta:,.2f}")

def consultar_ventas_rango():
    print("\n--- CONSULTAR VENTAS POR RANGO DE FECHAS ---")
    f_inicio = input("Fecha inicio (AAAA-MM-DD): ").strip()
    f_fin = input("Fecha fin (AAAA-MM-DD): ").strip()
    ventas = cargar_datos("ventas")

    ventas_filtradas = [
        v for v in ventas 
        if f_inicio <= v["fecha"].split(" ")[0] <= f_fin
    ]

    if not ventas_filtradas:
        print("No se encontraron ventas dentro del rango especificado.")
        return

    for v in ventas_filtradas:
        est = v.get("estado", "COMPLETADA")
        print(f"\nVenta ID: {v['id']} | Fecha: {v['fecha']} | Estado: [{est}] | Total: ${v['total']:,.2f}")
        for item in v["items"]:
            subt = item["cantidad"] * item["precio_unitario"]
            print(f"   - Prod: {item['codigo']} | Cant: {item['cantidad']} | P.U: ${item['precio_unitario']} | Subtotal: ${subt:,.2f}")

def devolver_venta():
    print("\n--- DEVOLUCIÓN DE VENTA ---")
    if not verificar_permisos(["ADMINISTRADOR", "INSTRUCTOR"]):
        return

    id_venta = input("Ingrese el ID de la venta a devolver (ej. V0001): ").strip().upper()
    ventas = cargar_datos("ventas")
    venta = next((v for v in ventas if v["id"] == id_venta), None)

    if not venta:
        print("Error: Venta no encontrada.")
        return
    if venta.get("estado") == "DEVUELTA":
        print("Error: Esta venta ya fue devuelta anteriormente.")
        return

    movimientos = cargar_datos("movimientos")
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")

    for item in venta["items"]:
        id_mov = f"M{len(movimientos)+1:04d}"
        movimientos.append({
            "id": id_mov,
            "producto_codigo": item["codigo"],
            "tipo": "ENTRADA",
            "cantidad": item["cantidad"],
            "motivo": f"Devolución Venta {id_venta}",
            "fecha": fecha_actual
        })

    venta["estado"] = "DEVUELTA"
    guardar_datos("movimientos", movimientos)
    guardar_datos("ventas", ventas)
    print(f"✓ Venta {id_venta} devuelta con éxito. Se reintegraron los productos al inventario.")

def exportar_inventario_csv():
    print("\n--- EXPORTAR INVENTARIO A CSV ---")
    productos = cargar_datos("productos")
    nombre_archivo = "reporte_inventario.csv"

    with open(nombre_archivo, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Codigo", "Nombre", "Categoria", "Unidad", "Costo", "Precio", "Stock_Actual", "Valor_Inventario_Venta"])
        
        for p in productos:
            if p["activo"]:
                stock = calcular_stock(p["codigo"])
                costo = p.get("costo", 0.0)
                writer.writerow([p["codigo"], p["nombre"], p["categoria"], p["unidad"], costo, p["precio"], stock, stock * p["precio"]])

    print(f"✓ Inventario exportado correctamente en '{nombre_archivo}'.")

def reporte_utilidad_estimada():
    print("\n--- REPORTE DE UTILIDAD ESTIMADA ---")
    if not verificar_permisos(["ADMINISTRADOR", "INSTRUCTOR"]):
        return

    ventas = cargar_datos("ventas")
    ingresos_totales = 0.0
    costos_totales = 0.0

    for v in ventas:
        if v.get("estado") != "DEVUELTA":
            for item in v["items"]:
                cant = item["cantidad"]
                precio = item["precio_unitario"]
                costo = item.get("costo_unitario", 0.0)
                ingresos_totales += cant * precio
                costos_totales += cant * costo

    utilidad_bruta = ingresos_totales - costos_totales
    print(f"Ingresos Totales por Ventas: ${ingresos_totales:,.2f}")
    print(f"Costo Total de Productos:    ${costos_totales:,.2f}")
    print("---------------------------------------------")
    print(f"Utilidad Estimada Bruta:     ${utilidad_bruta:,.2f}")

def alertas_stock():
    print("\n--- ALERTAS DE STOCK MÍNIMO ---")
    productos = cargar_datos("productos")
    alertas = False
    for p in productos:
        if p["activo"]:
            stock = calcular_stock(p["codigo"])
            if stock <= p["stock_minimo"]:
                print(f"ALERTA: [{p['codigo']}] {p['nombre']} -> Stock actual: {stock} | Mínimo: {p['stock_minimo']}")
                alertas = True
    if not alertas:
        print("Todos los productos activos superan el stock mínimo.")

def reporte_rotacion_productos():
    print("\n--- REPORTE DE ROTACIÓN DE PRODUCTOS ---")
    ventas = cargar_datos("ventas")
    productos = cargar_datos("productos")
    
    rotacion = {}
    for v in ventas:
        if v.get("estado") != "DEVUELTA":
            for item in v["items"]:
                code = item["codigo"]
                rotacion[code] = rotacion.get(code, 0) + item["cantidad"]
            
    if not rotacion:
        print("No hay ventas registradas para calcular rotación.")
        return

    print("Unidades vendidas por producto:")
    for code, cant in sorted(rotacion.items(), key=lambda x: x[1], reverse=True):
        p = next((prod for prod in productos if prod["codigo"] == code), None)
        nombre = p["nombre"] if p else "Desconocido"
        print(f"- {nombre} ({code}): {cant} unidades")

def generar_reportes():
    print("\n--- REPORTES DEL SISTEMA ---")
    productos = cargar_datos("productos")
    ventas = cargar_datos("ventas")

    valor_total_inv = sum(calcular_stock(p["codigo"]) * p["precio"] for p in productos if p["activo"])
    print(f"1. Valor total del inventario (precio de venta): ${valor_total_inv:,.2f}")

    ventas_validas = [v for v in ventas if v.get("estado") != "DEVUELTA"]
    total_ingresos = sum(v["total"] for v in ventas_validas)
    unidades_vendidas = sum(item["cantidad"] for v in ventas_validas for item in v["items"])
    print(f"2. Total Ventas: {len(ventas_validas)} | Unidades Vendidas: {unidades_vendidas} | Ingresos Acumulados: ${total_ingresos:,.2f}")

    conteo_productos = {}
    for v in ventas_validas:
        for item in v["items"]:
            c = item["codigo"]
            conteo_productos[c] = conteo_productos.get(c, 0) + item["cantidad"]
    
    ranking = sorted(conteo_productos.items(), key=lambda x: x[1], reverse=True)[:3]
    print("\n3. Top 3 productos más vendidos:")
    for codigo, cant in ranking:
        p = next((prod for prod in productos if prod["codigo"] == codigo), None)
        nombre = p["nombre"] if p else "Desconocido"
        print(f"   - {nombre} ({codigo}): {cant} unidades")

def menu():
    inicializar_almacenamiento()
    if not iniciar_sesion():
        print("Acceso denegado. Cerrando AgroControl CBA...")
        return

    while True:
        print(f"\n==================== AGROCONTROL CBA [{USUARIO_ACTUAL['rol']}] ====================")
        print("1. Registrar producto")
        print("2. Consultar/Listar productos")
        print("3. Desactivar producto")
        print("4. Registrar lote productivo")
        print("5. Cosechar lote")
        print("6. Movimiento manual de inventario")
        print("7. Registrar venta")
        print("8. Consultar ventas por rango de fechas")
        print("9. Devolución de venta (Admin/Instructor)")
        print("10. Exportar inventario a CSV")
        print("11. Reporte de utilidad estimada (Admin/Instructor)")
        print("12. Alertas de stock mínimo")
        print("13. Reportes del sistema")
        print("14. Reporte de rotación de productos")
        print("0. Salir")
        print("=========================================================")
        
        opcion = input("Seleccione una opción: ").strip()
        try:
            if opcion == "1":
                registrar_producto()
            elif opcion == "2":
                listar_productos()
            elif opcion == "3":
                desactivar_producto()
            elif opcion == "4":
                registrar_lote()
            elif opcion == "5":
                cosechar_lote()
            elif opcion == "6":
                registrar_movimiento_manual()
            elif opcion == "7":
                registrar_venta()
            elif opcion == "8":
                consultar_ventas_rango()
            elif opcion == "9":
                devolver_venta()
            elif opcion == "10":
                exportar_inventario_csv()
            elif opcion == "11":
                reporte_utilidad_estimada()
            elif opcion == "12":
                alertas_stock()
            elif opcion == "13":
                generar_reportes()
            elif opcion == "14":
                reporte_rotacion_productos()
            elif opcion == "0":
                print("Saliendo de AgroControl CBA...")
                break
            else:
                print("Opción no válida.")
        except Exception as e:
            print(f"Error inesperado: {e}")

if __name__ == "__main__":
    menu()