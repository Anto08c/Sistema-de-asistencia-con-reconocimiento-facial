from datetime import datetime
import numpy as np
from backend.conexion import obtener_conexion

def registrar_asistencia(empleado_id, tipo):
    if tipo not in ("entrada", "salida"):
        return False, "Tipo de asistencia no válido."

    ahora = datetime.now()
    fecha = ahora.date()
    hora = ahora.time().replace(microsecond=0)

    conexion = obtener_conexion()

    try:
        # Iniciar una transacción para evitar marcaciones simultáneas.
        conexion.begin()

        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT id
                FROM empleados
                WHERE id = %s AND estado = 'activo'
                FOR UPDATE
                """,
                (empleado_id,)
            )

            empleado = cursor.fetchone()

            if empleado is None:
                conexion.rollback()
                return False, "El empleado no existe o está inactivo."

            cursor.execute(
                """
                SELECT tipo
                FROM asistencias
                WHERE empleado_id = %s AND fecha = %s
                ORDER BY hora DESC, id DESC
                LIMIT 1
                """,
                (empleado_id, fecha)
            )

            ultima = cursor.fetchone()

            if ultima is None:
                if tipo == "salida":
                    conexion.rollback()
                    return False, "Primero debes registrar una entrada."

            elif ultima["tipo"] == tipo:
                conexion.rollback()

                if tipo == "entrada":
                    return False, (
                        "Ya registraste una entrada. "
                        "Debes registrar una salida antes de volver a entrar."
                    )

                return False, (
                    "Ya registraste una salida. "
                    "Debes registrar una entrada antes de volver a salir."
                )

            cursor.execute(
                """
                INSERT INTO asistencias
                    (empleado_id, fecha, hora, tipo, metodo)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (empleado_id, fecha, hora, tipo, "facial")
            )

        conexion.commit()

        return True, (
            f"{tipo.capitalize()} registrada a las "
            f"{hora.strftime('%H:%M:%S')}."
        )

    except Exception as error:
        conexion.rollback()
        print("Error al registrar asistencia:", error)
        return False, "No se pudo registrar la asistencia."

    finally:
        conexion.close()


def listar_asistencias():
    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    e.codigo,
                    e.nombres,
                    e.apellidos,
                    a.fecha,
                    a.hora,
                    a.tipo,
                    a.metodo
                FROM asistencias a
                INNER JOIN empleados e
                    ON e.id = a.empleado_id
                ORDER BY a.fecha DESC, a.hora DESC, a.id DESC
                """
            )

            registros = cursor.fetchall()

            for registro in registros:
                if registro["fecha"] is not None:
                    registro["fecha"] = registro["fecha"].isoformat()

                if registro["hora"] is not None:
                    registro["hora"] = str(registro["hora"])

            return registros

    finally:
        conexion.close()


def cargar_rostros_registrados():
    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    e.id,
                    e.codigo,
                    e.nombres,
                    e.apellidos,
                    r.embedding
                FROM empleados e
                INNER JOIN rostros r ON r.empleado_id = e.id
                WHERE e.estado = 'activo'
                """
            )

            registros = cursor.fetchall()

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
                    registro["nombres"] + " " +
                    registro["apellidos"]
                ),
                "embedding": embedding
            })

        return empleados

    finally:
        conexion.close()


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

