import cv2
# Abrir la cámara
camara = cv2.VideoCapture(0)
# Modelo para detectar rostros
detector = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)
while True:
    # Leer imagen de la cámara
    correcto, imagen = camara.read()
    if not correcto:
        print("No se pudo acceder a la cámara")
        break
    # Convertir la imagen a escala de grises
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    # Detectar rostros
    rostros = detector.detectMultiScale(
        gris,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(50, 50)
    )
    # Dibujar un rectángulo alrededor de cada rostro
    for (x, y, ancho, alto) in rostros:
        cv2.rectangle(
            imagen,
            (x, y),
            (x + ancho, y + alto),
            (0, 255, 0),
            2
        )
        cv2.putText(
            imagen,
            "Rostro detectado",
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )
    # Mostrar cámara
    cv2.imshow("Laboratorio 01 - Deteccion facial", imagen)

    # Presionar ESC para salir
    if cv2.waitKey(1) & 0xFF == 27:
        break
# Liberar cámara
camara.release()
cv2.destroyAllWindows()