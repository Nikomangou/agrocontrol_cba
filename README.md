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
```text
agrocontrol_cba/
│   main.py
│   README.md
│   .gitignore
└── data/
    ├── productos.json
    ├── lotes.json
    ├── movimientos.json
    └── ventas.json

## Instrucciones de Ejecución

Clonar el repositorio:
 
git clone [https://github.com/Nikomangou/agrocontrol_cba.git](https://github.com/Nikomangou/agrocontrol_cba.git)
cd agrocontrol_cba

## Ejecutar la aplicación:

python main.py

## Reglas de Negocio Principales

* **Códigos Únicos:** Los códigos de producto y lotes se almacenan en mayúsculas y no pueden duplicarse.

* **Cálculo de Stock:** El inventario no se guarda de forma aislada; se calcula dinámicamente a partir del historial de movimientos de entrada y salida.

* **Control de Ventas y Salidas:** Ninguna venta o salida manual puede dejar el inventario en valores negativos.

* **Cosechas Únicas:** Un lote en estado EN_PRODUCCION solo puede cosecharse una vez, generando automáticamente un movimiento de entrada al inventario.

* **Desactivación Lógica:** Los productos inactivos no se eliminan físicamente para preservar el historial de movimientos y ventas.