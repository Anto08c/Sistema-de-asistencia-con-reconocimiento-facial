import cv2
import insightface

print("Cargando InsightFace con liveness...")

modelo = insightface.app.FaceAnalysis(
    name="buffalo_l",
    addons=["liveness"],
    liveness_mode="normal",
    liveness_threshold=0.8
)

modelo.prepare(
    ctx_id=0,
    det_size=(640, 640)
)

print("✅ Modelo de liveness cargado")

camara = cv2.VideoCapture(0)

if not camara.isOpened():
    print("❌ No se pudo abrir la cámara")
    exit()

print("✅ Cámara abierta")
print("Presiona ESC para salir")

while True:

    correcto, imagen = camara.read()

    if not correcto:
        print("❌ No se pudo leer la cámara")
        break

    imagen = cv2.flip(imagen, 1)

    rostros = modelo.get(imagen)

    for rostro in rostros:

        # Coordenadas del rostro
        x1, y1, x2, y2 = map(int, rostro.bbox)

        # Resultado de liveness
        resultado = rostro.liveness

        if resultado is None:

            texto = "Liveness no disponible"
            estado = "DESCONOCIDO"

        elif resultado.status == "input_rejected":

            texto = "Entrada rechazada"
            estado = "RECHAZADO"

        elif resultado.is_live:

            texto = f"REAL - {resultado.live_score:.2f}"
            estado = "PERSONA REAL"

        else:

            texto = f"FALSA - {resultado.live_score:.2f}"
            estado = "POSIBLE FOTO"

        # Cuadro del rostro
        cv2.rectangle(
            imagen,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2
        )

        # Estado
        cv2.putText(
            imagen,
            estado,
            (x1, y1 - 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        # Score
        cv2.putText(
            imagen,
            texto,
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

    cv2.imshow(
        "Laboratorio 04 - Liveness Oficial",
        imagen
    )

    if cv2.waitKey(1) & 0xFF == 27:
        break

camara.release()
cv2.destroyAllWindows()