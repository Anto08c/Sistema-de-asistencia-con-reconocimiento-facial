
import sqlite3
from pathlib import Path

# Ubicación de la base de datos
RUTA_BD = Path(__file__).resolve().parent.parent / "datos" / "asistencia.db"


def conectar():
    conexion = sqlite3.connect(RUTA_BD)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion


def registrar_empleado(codigo, nombres, apellidos):
    codigo = codigo.strip().upper()
    nombres = nombres.strip()
    apellidos = apellidos.strip()

    if not codigo or not nombres or not apellidos:
        return False, "Todos los campos son obligatorios."

    try:
        with conectar() as conexion:
            conexion.execute(
                """
                INSERT INTO empleados (codigo, nombres, apellidos)
                VALUES (?, ?, ?)
                """,
                (codigo, nombres, apellidos)
            )

        return True, "Empleado registrado correctamente."

    except sqlite3.IntegrityError:
        return False, "El código ya existe o los datos no son válidos."


def listar_empleados():
    with conectar() as conexion:
        empleados = conexion.execute(
            """
            SELECT id, codigo, nombres, apellidos, estado
            FROM empleados
            ORDER BY id DESC
            """
        ).fetchall()

    return [dict(empleado) for empleado in empleados]


def cambiar_estado_empleado(empleado_id, nuevo_estado):
    if nuevo_estado not in ("activo", "inactivo"):
        return False, "Estado no válido."

    with conectar() as conexion:
        cursor = conexion.execute(
            """
            UPDATE empleados
            SET estado = ?
            WHERE id = ?
            """,
            (nuevo_estado, empleado_id)
        )

        if cursor.rowcount == 0:
            return False, "No se encontró el empleado."

    return True, "Estado actualizado correctamente."