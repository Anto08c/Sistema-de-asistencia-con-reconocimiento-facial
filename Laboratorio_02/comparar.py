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
# 2. FUNCIÓN PARA OBTENER EL EMBEDDING
# ==========================================================

def obtener_embedding(ruta):

    imagen = cv2.imread(ruta)

    if imagen is None:
        print(f"No se pudo cargar: {ruta}")
        return None

    rostros = modelo.get(imagen)

    if len(rostros) == 0:
        print(f"No se encontró ningún rostro en: {ruta}")
        return None

    if len(rostros) > 1:
        print(f"Se encontraron varios rostros en: {ruta}")
        return None

    return rostros[0].embedding


# ==========================================================
# 3. OBTENER LOS DOS EMBEDDINGS
# ==========================================================

embedding_registrado = obtener_embedding(
    "rostros/anto.jpeg"
)

embedding_prueba = obtener_embedding(
    "rostros/otra_persona.png"
)


if embedding_registrado is None or embedding_prueba is None:
    exit()


# ==========================================================
# 4. NORMALIZAR
# ==========================================================

embedding_registrado = embedding_registrado / np.linalg.norm(
    embedding_registrado
)

embedding_prueba = embedding_prueba / np.linalg.norm(
    embedding_prueba
)


# ==========================================================
# 5. CALCULAR SIMILITUD
# ==========================================================

similitud = np.dot(
    embedding_registrado,
    embedding_prueba
)


print("-----------------------------------")
print("COMPARACIÓN FACIAL")
print("-----------------------------------")

print("Similitud:", similitud)