
import sqlite3
from pathlib import Path

# Ruta de la base de datos
CARPETA_DATOS = Path(__file__).resolve().parent.parent / "datos"
CARPETA_DATOS.mkdir(exist_ok=True)

RUTA_BD = CARPETA_DATOS / "asistencia.db"

# Conectar con SQLite
conexion = sqlite3.connect(RUTA_BD)
cursor = conexion.cursor()

# Activar las relaciones entre tablas
cursor.execute("PRAGMA foreign_keys = ON")

# Tabla de empleados
cursor.execute("""
CREATE TABLE IF NOT EXISTS empleados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL UNIQUE,
    nombres TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    estado TEXT NOT NULL DEFAULT 'activo'
        CHECK (estado IN ('activo', 'inactivo')),
    fecha_registro TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)
""")

# Tabla de representaciones faciales
cursor.execute("""
CREATE TABLE IF NOT EXISTS rostros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empleado_id INTEGER NOT NULL,
    embedding BLOB NOT NULL,
    fecha_registro TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (empleado_id)
        REFERENCES empleados(id)
        ON DELETE CASCADE
)
""")

# Tabla de asistencias
cursor.execute("""
CREATE TABLE IF NOT EXISTS asistencias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empleado_id INTEGER NOT NULL,
    fecha TEXT NOT NULL,
    hora TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('entrada', 'salida')),
    metodo TEXT NOT NULL DEFAULT 'facial',
    FOREIGN KEY (empleado_id)
        REFERENCES empleados(id)
)
""")

conexion.commit()
conexion.close()

print("Base de datos creada correctamente.")
print("Ubicación:", RUTA_BD)