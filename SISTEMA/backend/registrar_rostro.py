
import sqlite3
from pathlib import Path

import cv2
import numpy as np
from insightface.app import FaceAnalysis

# Ubicación de la base de datos
RUTA_BD = (
    Path(__file__).resolve().parent.parent
    / "datos"
    / "asistencia.db"
)

# Cargar el modelo de reconocimiento facial
modelo = FaceAnalysis(
    name="buffalo_l",
    providers=["CPUExecutionProvider"]
)
modelo.prepare(ctx_id=0, det_size=(640, 640))


def registrar_rostro():
    codigo = input("Código del empleado: ").strip().upper()

    # Buscar al empleado y comprobar que esté activo
    with sqlite3.connect(RUTA_BD) as conexion:
        conexion.execute("PRAGMA foreign_keys = ON")

        empleado = conexion.execute(
            """
            SELECT id, nombres, apellidos
            FROM empleados
            WHERE codigo = ? AND estado = 'activo'
            """,
            (codigo,)
        ).fetchone()

    if empleado is None:
        print("No existe un empleado activo con ese código.")
        return

    empleado_id, nombres, apellidos = empleado
    print(f"Empleado: {nombres} {apellidos}")
    print("Coloca tu rostro frente a la cámara.")
    print("Presiona ESPACIO para capturar o ESC para cancelar.")

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

            if tecla == 27:  # ESC para cancelar
                break

            if tecla == 32:  # ESPACIO para capturar
                if len(rostros) != 1:
                    print(
                        "Debe aparecer exactamente un rostro. "
                        "Intenta nuevamente."
                    )
                    continue

                embedding = rostros[0].normed_embedding
                embedding_guardado = np.asarray(
                    embedding, dtype=np.float32
                )
                break

    finally:
        camara.release()
        cv2.destroyAllWindows()

    if embedding_guardado is None:
        print("Registro facial cancelado o no completado.")
        return

    # Guardar el embedding asociado al empleado
    with sqlite3.connect(RUTA_BD) as conexion:
        conexion.execute(
            """
            INSERT INTO rostros (empleado_id, embedding)
            VALUES (?, ?)
            """,
            (
                empleado_id,
                sqlite3.Binary(embedding_guardado.tobytes())
            )
        )

    print("Rostro registrado correctamente.")


if __name__ == "__main__":
    registrar_rostro()