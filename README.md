# AgroControl CBA 

**Sistema monolítico para la gestión de producción, inventario y ventas**  
*Centro de Biotecnología Agropecuaria (CBA - Facatativá)*  
**Programa:** Técnico en Programación de Software  
**Estudiante:** Nicole Sthephanie Alonso Mayorga 

##  Descripción del Proyecto
AgroControl CBA es una aplicación de consola monolítica desarrollada en Python que centraliza el control de productos comercializables, lotes productivos, movimientos de inventario (entradas/salidas) y registro de ventas. Conserva la información de forma local mediante archivos JSON y gestiona el historial de cambios utilizando Git y GitHub.

##  Tecnologías Utilizadas
* **Lenguaje:** Python 3.x (Módulos estándar: `json`, `os`, `datetime`)
* **Persistencia:** Archivos JSON
* **Control de Versiones:** Git y GitHub


## Estructura del Proyecto
agrocontrol_cba/
│   main.py
│   README.md
│   .gitignore
│   reporte_inventario.csv
└── data/
    ├── productos.json
    ├── lotes.json
    ├── movimientos.json
    ├── ventas.json
    ├── usuarios.json
    └── backups/

## Instrucciones de Ejecución

Clonar el repositorio:
 
git clone [https://github.com/Nikomangou/agrocontrol_cba.git](https://github.com/Nikomangou/agrocontrol_cba.git)
cd agrocontrol_cba

## Ejecutar la aplicación:
Admin: Usuario admin | Contraseña admin123

Operador: Usuario operador | Contraseña operador123

python main.py

## Reglas de Negocio Principales

* **Códigos Únicos:** Los códigos de producto y lotes se almacenan en mayúsculas y no pueden duplicarse.

* **Cálculo de Stock:** El inventario no se guarda de forma aislada; se calcula dinámicamente a partir del historial de movimientos de entrada y salida.

* **Control de Ventas y Salidas:** Ninguna venta o salida manual puede dejar el inventario en valores negativos.

* **Cosechas Únicas:** Un lote en estado EN_PRODUCCION solo puede cosecharse una vez, generando automáticamente un movimiento de entrada al inventario.

* **Desactivación Lógica:** Los productos inactivos no se eliminan físicamente para preservar el historial de movimientos y ventas.

## Retos de Ampliación Implementados

* **Autenticación y Roles:** Inicio de sesión con gestión de permisos para usuarios con rol `OPERADOR` e `INSTRUCTOR`/`ADMINISTRADOR`.
* **Respaldos Automáticos:** Copias de seguridad automáticas con marca de tiempo guardadas en `data/backups/` antes de cada modificación.
* **Margen de Ganancia y Utilidad:** Control de costos unitarios e informe de utilidad bruta estimada sobre las ventas acumuladas.
* **Filtros por Fecha:** Consulta avanzada de historial de ventas delimitada por rango de fechas (`AAAA-MM-DD`).
* **Gestión de Devoluciones:** Proceso de reversión de ventas que reintegra automáticamente el stock al inventario como movimiento de entrada.
* **Exportación de Datos:** Generación del reporte de inventario completo en formato CSV (`reporte_inventario.csv`).