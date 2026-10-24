
import csv
import io

from backend.conexion import obtener_conexion


def generar_csv_asistencias(
    fecha_desde,
    fecha_hasta
):
    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        consulta = """
            SELECT
                e.codigo AS codigo,
                CONCAT(e.nombres, ' ', e.apellidos) AS empleado,
                a.fecha AS fecha,
                a.hora AS hora,
                a.tipo AS tipo
            FROM asistencias a
            INNER JOIN empleados e
                ON e.id = a.empleado_id
            WHERE a.fecha >= %s
              AND a.fecha <= %s
            ORDER BY a.fecha ASC, a.hora ASC, a.id ASC
        """

        cursor.execute(
            consulta,
            (fecha_desde, fecha_hasta)
        )

        registros = cursor.fetchall()

        # Preparar el contenido CSV compatible con Excel
        archivo = io.StringIO(newline="")
        archivo.write("\ufeff")

        escritor = csv.writer(
            archivo,
            delimiter=";"
        )

        escritor.writerow([
            "Código",
            "Empleado",
            "Fecha",
            "Hora",
            "Tipo"
        ])

        for registro in registros:
            escritor.writerow([
                registro["codigo"],
                registro["empleado"],
                registro["fecha"],
                registro["hora"],
                registro["tipo"]
            ])

        contenido = archivo.getvalue().encode("utf-8")
        archivo.close()

        return contenido 

    finally:
        if cursor is not None:
            cursor.close()

        if conexion is not None:
            conexion.close()


