
import cv2
import numpy as np

from insightface.app import FaceAnalysis
from backend.asistencia import (
    registrar_asistencia,
    cargar_rostros_registrados
)

UMBRAL_SIMILITUD = 0.45


