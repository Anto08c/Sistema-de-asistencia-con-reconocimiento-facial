import cv2
import insightface
import numpy as np

# ==========================================================
# 1. CARGAR MODELO
# ==========================================================

modelo = insightface.app.FaceAnalysis(
    name="buffalo_l"
)

modelo.prepare(
    ctx_id=0,
    det_size=(640, 640)
)


# ==========================================================
# 2. PERSONAS REGISTRADAS
# ==========================================================

personas = {
    "Alma": "rostros/anto.jpeg",
    "Otra persona": "rostros/otra_persona.png"
}


# ==========================================================
# 3. GENERAR EMBEDDINGS DE LAS PERSONAS
# ==========================================================

embeddings_registrados = {}

for nombre, ruta in personas.items():

    imagen = cv2.imread(ruta)

    if imagen is None:
        print(f"No se pudo cargar: {ruta}")
        continue

    rostros = modelo.get(imagen)

    if len(rostros) != 1:
        print(f"La imagen de {nombre} debe contener exactamente un rostro.")
        continue

    embedding = rostros[0].embedding

    # Normalización
    embedding = embedding / np.linalg.norm(embedding)

    embeddings_registrados[nombre] = embedding


print("Personas registradas:")

for nombre in embeddings_registrados:
    print("-", nombre)


# ==========================================================
# 4. ABRIR CÁMARA
# ==========================================================

camara = cv2.VideoCapture(0)

if not camara.isOpened():
    print("No se pudo abrir la cámara.")
    exit()


# ==========================================================
# 5. RECONOCIMIENTO EN TIEMPO REAL
# ==========================================================

while True:

    correcto, imagen = camara.read()

    if not correcto:
        print("No se pudo leer la cámara.")
        break

    rostros = modelo.get(imagen)

    for rostro in rostros:

        # ----------------------------------------------
        # Obtener embedding del rostro actual
        # ----------------------------------------------

        embedding_actual = rostro.embedding

        embedding_actual = embedding_actual / np.linalg.norm(
            embedding_actual
        )


        # ----------------------------------------------
        # Buscar la persona más parecida
        # ----------------------------------------------

        mejor_nombre = "Desconocido"
        mejor_similitud = -1

        for nombre, embedding_registrado in embeddings_registrados.items():

            similitud = np.dot(
                embedding_registrado,
                embedding_actual
            )

            if similitud > mejor_similitud:

                mejor_similitud = similitud
                mejor_nombre = nombre


        # ----------------------------------------------
        # Umbral provisional
        # ----------------------------------------------

        umbral = 0.45

        if mejor_similitud >= umbral:

            texto = f"{mejor_nombre} ({mejor_similitud:.2f})"

        else:

            texto = f"Desconocido ({mejor_similitud:.2f})"


        # ----------------------------------------------
        # Dibujar rostro
        # ----------------------------------------------

        x1, y1, x2, y2 = rostro.bbox.astype(int)

        cv2.rectangle(
            imagen,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2
        )

        cv2.putText(
            imagen,
            texto,
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )


    # Mostrar cámara

    cv2.imshow(
        "Sistema de reconocimiento facial",
        imagen
    )


    # ESC para salir

    if cv2.waitKey(1) & 0xFF == 27:
        break


# ==========================================================
# 6. CERRAR
# ==========================================================

camara.release()
cv2.destroyAllWindows()