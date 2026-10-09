
import sqlite3
from pathlib import Path
from datetime import datetime

RUTA_BD = (
    Path(__file__).resolve().parent.parent
    / "datos"
    / "asistencia.db"
)


def registrar_asistencia(empleado_id, tipo):
    if tipo not in ("entrada", "salida"):
        return False, "Tipo de asistencia no válido."

    ahora = datetime.now()
    fecha = ahora.strftime("%Y-%m-%d")
    hora = ahora.strftime("%H:%M:%S")

    with sqlite3.connect(RUTA_BD) as conexion:
        conexion.execute("PRAGMA foreign_keys = ON")

        empleado = conexion.execute(
            """
            SELECT id
            FROM empleados
            WHERE id = ? AND estado = 'activo'
            """,
            (empleado_id,)
        ).fetchone()

        if empleado is None:
            return False, "El empleado no existe o está inactivo."

        registros = conexion.execute(
            """
            SELECT tipo
            FROM asistencias
            WHERE empleado_id = ? AND fecha = ?
            ORDER BY id
            """,
            (empleado_id, fecha)
        ).fetchall()

        tipos = [registro[0] for registro in registros]

        if tipo == "entrada":
            if "entrada" in tipos:
                return False, "La entrada de hoy ya está registrada."

        elif tipo == "salida":
            if "entrada" not in tipos:
                return False, "Primero debes registrar la entrada."

            if "salida" in tipos:
                return False, "La salida de hoy ya está registrada."

        conexion.execute(
            """
            INSERT INTO asistencias
                (empleado_id, fecha, hora, tipo, metodo)
            VALUES (?, ?, ?, ?, ?)
            """,
            (empleado_id, fecha, hora, tipo, "facial")
        )

    return True, f"{tipo.capitalize()} registrada a las {hora}."


def listar_asistencias():
    with sqlite3.connect(RUTA_BD) as conexion:
        conexion.row_factory = sqlite3.Row

        registros = conexion.execute(
            """
            SELECT
                e.codigo,
                e.nombres,
                e.apellidos,
                a.fecha,
                a.hora,
                a.tipo
            FROM asistencias a
            INNER JOIN empleados e ON e.id = a.empleado_id
            ORDER BY a.id DESC
            """
        ).fetchall()

    return [dict(registro) for registro in registros]


def cargar_rostros_registrados():
    """Carga los embeddings de los empleados activos."""

    import numpy as np

    with sqlite3.connect(RUTA_BD) as conexion:
        conexion.row_factory = sqlite3.Row

        registros = conexion.execute(
            """
            SELECT
                e.id,
                e.codigo,
                e.nombres,
                e.apellidos,
                r.embedding
            FROM empleados e
            INNER JOIN rostros r ON e.id = r.empleado_id
            WHERE e.estado = 'activo'
            """
        ).fetchall()

    empleados = []

    for registro in registros:
        embedding = np.frombuffer(
            registro["embedding"],
            dtype=np.float32
        ).copy()

        if embedding.shape != (512,):
            continue

        empleados.append({
            "id": registro["id"],
            "codigo": registro["codigo"],
            "nombre": (
                registro["nombres"] + " " + registro["apellidos"]
            ),
            "embedding": embedding
        })

    return empleados


if __name__ == "__main__":
    print("=== HISTORIAL DE ASISTENCIAS ===")

    for registro in listar_asistencias():
        print(
            registro["codigo"],
            registro["nombres"],
            registro["apellidos"],
            registro["fecha"],
            registro["hora"],
            registro["tipo"]
        )

