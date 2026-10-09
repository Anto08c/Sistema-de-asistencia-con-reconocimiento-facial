import cv2
import insightface

# Crear el modelo
modelo = insightface.app.FaceAnalysis(
    name="buffalo_l"
)

# Preparar el modelo para CPU
modelo.prepare(ctx_id=0, det_size=(640, 640))

# Cargar imagen
imagen = cv2.imread("rostros/anto.jpeg")

if imagen is None:
    print("❌ No se pudo cargar la imagen.")
    exit()

# Detectar rostros
rostros = modelo.get(imagen)

print("Rostros encontrados:", len(rostros))

for i, rostro in enumerate(rostros):

    print(f"\nRostro {i + 1}")

    print("Bounding box:")
    print(rostro.bbox)

    print("Embedding:")
    print(rostro.embedding[:10])

    print("Tamaño del embedding:")
    print(len(rostro.embedding))