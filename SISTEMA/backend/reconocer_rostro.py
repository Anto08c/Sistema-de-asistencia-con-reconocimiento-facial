
import cv2
import numpy as np

from insightface.app import FaceAnalysis
from asistencia import registrar_asistencia, cargar_rostros_registrados

UMBRAL_SIMILITUD = 0.45


def reconocer_y_marcar():
    empleados = cargar_rostros_registrados()

    if not empleados:
        print("No hay empleados con rostros registrados.")
        return

    modelo = FaceAnalysis(
        name="buffalo_l",
        providers=["CPUExecutionProvider"]
    )
    modelo.prepare(ctx_id=0, det_size=(640, 640))

    camara = cv2.VideoCapture(0)

    if not camara.isOpened():
        print("No se pudo abrir la cámara.")
        return

    empleado_reconocido = None
    similitud_actual = 0.0
    mensaje = "Buscando rostro..."
    color_mensaje = (255, 255, 255)

    print("Sistema de asistencia iniciado.")
    print("E = registrar entrada | S = registrar salida")
    print("ESC = cerrar el sistema")

    try:
        while True:
            correcto, frame = camara.read()

            if not correcto:
                print("No se pudo leer la cámara.")
                break

            rostros = modelo.get(frame)

            # Solo procesar cuando aparezca exactamente un rostro
            empleado_reconocido = None
            similitud_actual = 0.0

            if len(rostros) == 1:
                rostro = rostros[0]
                embedding = np.asarray(
                    rostro.normed_embedding,
                    dtype=np.float32
                )

                mejor_empleado = None
                mejor_similitud = -1.0

                for empleado in empleados:
                    similitud = float(
                        np.dot(embedding, empleado["embedding"])
                    )

                    if similitud > mejor_similitud:
                        mejor_similitud = similitud
                        mejor_empleado = empleado

                similitud_actual = mejor_similitud

                x1, y1, x2, y2 = map(int, rostro.bbox)

                if mejor_similitud >= UMBRAL_SIMILITUD:
                    empleado_reconocido = mejor_empleado

                    texto = (
                        f"{mejor_empleado['nombre']} "
                        f"({mejor_empleado['codigo']})"
                    )
                    color = (0, 200, 0)
                    mensaje = "E: Entrada | S: Salida"
                    color_mensaje = (0, 200, 0)
                else:
                    texto = "Rostro no reconocido"
                    color = (0, 0, 255)
                    mensaje = "Empleado no identificado"
                    color_mensaje = (0, 0, 255)

                cv2.rectangle(
                    frame, (x1, y1), (x2, y2), color, 2
                )
                cv2.putText(
                    frame,
                    texto,
                    (x1, max(y1 - 10, 25)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    color,
                    2
                )

            elif len(rostros) > 1:
                mensaje = "Debe aparecer una sola persona"
                color_mensaje = (0, 0, 255)
            else:
                mensaje = "Buscando rostro..."
                color_mensaje = (255, 255, 255)

            cv2.putText(
                frame,
                mensaje,
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                color_mensaje,
                2
            )

            if len(rostros) == 1:
                cv2.putText(
                    frame,
                    f"Similitud: {similitud_actual:.3f}",
                    (20, 65),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 0),
                    2
                )

            cv2.imshow("Sistema de asistencia facial", frame)

            tecla = cv2.waitKey(1) & 0xFF

            if tecla == 27:  # ESC
                break

            # Solo marcar si el empleado fue reconocido
            if empleado_reconocido is not None:
                if tecla == ord("e"):
                    correcto, mensaje_resultado = registrar_asistencia(
                        empleado_reconocido["id"],
                        "entrada"
                    )
                    print(mensaje_resultado)

                elif tecla == ord("s"):
                    correcto, mensaje_resultado = registrar_asistencia(
                        empleado_reconocido["id"],
                        "salida"
                    )
                    print(mensaje_resultado)

    finally:
        camara.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    reconocer_y_marcar()
