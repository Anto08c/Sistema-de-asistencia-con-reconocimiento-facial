
import cv2
import numpy as np

from insightface.app import FaceAnalysis
from backend.conexion import obtener_conexion


modelo = FaceAnalysis(
    name="buffalo_l",
    providers=["CPUExecutionProvider"]
)
modelo.prepare(ctx_id=0, det_size=(640, 640))


def registrar_rostro():
    codigo = input("Código del empleado: ").strip().upper()

    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, nombres, apellidos
                FROM empleados
                WHERE codigo = %s AND estado = 'activo'
                """,
                (codigo,)
            )
            empleado = cursor.fetchone()

    finally:
        conexion.close()

    if empleado is None:
        print("No existe un empleado activo con ese código.")
        return

    empleado_id = empleado["id"]

    print(
        "Empleado:",
        empleado["nombres"],
        empleado["apellidos"]
    )
    print("Coloca tu rostro frente a la cámara.")
    print("ESPACIO = capturar | ESC = cancelar")

    camara = cv2.VideoCapture(0)

    if not camara.isOpened():
        print("No se pudo abrir la cámara.")
        return

    embedding_guardado = None

    try:
        while True:
            correcto, frame = camara.read()

            if not correcto:
                print("No se pudo leer la cámara.")
                break

            rostros = modelo.get(frame)

            for rostro in rostros:
                x1, y1, x2, y2 = map(int, rostro.bbox)
                cv2.rectangle(
                    frame, (x1, y1), (x2, y2), (0, 255, 0), 2
                )

            cv2.putText(
                frame,
                f"Rostros detectados: {len(rostros)}",
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

            cv2.imshow("Registro facial", frame)
            tecla = cv2.waitKey(1) & 0xFF

            if tecla == 27:
                break

            if tecla == 32:
                if len(rostros) != 1:
                    print("Debe aparecer exactamente un rostro.")
                    continue

                embedding_guardado = np.asarray(
                    rostros[0].normed_embedding,
                    dtype=np.float32
                ).copy()
                break

    finally:
        camara.release()
        cv2.destroyAllWindows()

    if embedding_guardado is None:
        print("Registro facial cancelado o no completado.")
        return

    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO rostros (empleado_id, embedding)
                VALUES (%s, %s)
                """,
                (empleado_id, embedding_guardado.tobytes())
            )

        conexion.commit()
        print("Rostro registrado correctamente en MySQL.")

    except Exception as error:
        conexion.rollback()
        print("Error al guardar el rostro:", error)

    finally:
        conexion.close()


if __name__ == "__main__":
    registrar_rostro()
