import cv2
import insightface                                     
import numpy as np

print("================================")
print(" SISTEMA DE ASISTENCIA FACIAL")
print("================================")

print("OpenCV:", cv2.__version__)
print("InsightFace:", insightface.__version__)
print("NumPy:", np.__version__)

print()
print("Cargando modelo facial...")

modelo = insightface.app.FaceAnalysis(
    name="buffalo_l"
)

modelo.prepare(
    ctx_id=0,
    det_size=(640, 640)
)

print("✅ Modelo facial cargado correctamente")
print("✅ Sistema base funcionando")
