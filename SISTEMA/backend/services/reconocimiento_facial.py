"""Procesamiento de imagenes y comparación de embeddings faciales."""
import base64

import cv2
import numpy as np
from fastapi import HTTPException
from insightface.app import FaceAnalysis

from backend.conexion import obtener_conexion

UMBRAL_SIMILITUD = 0.45

analizador_facial = FaceAnalysis(
    name="buffalo_l",
    providers=["CPUExecutionProvider"],
    addons=["liveness"],
    liveness_mode="normal", #Valida antes del embedding
    liveness_threshold=0.8,
)
analizador_facial.prepare(ctx_id=0, det_size=(640, 640))

def obtener_embedding_de_imagen(imagen_base64: str) -> np.ndarray:
    """Decodifica una imagen BASE 64 y devuelve el embedding de un solo rostro."""
    try:
        contenido = base64.b64decode(imagen_base64.split(",")[-1], validate=True)
    except Exception as error:
        raise HTTPException(status_code=400, detail="La imagen enviada no tiene un formato válido.",
    ) from error

    arreglo = np.frombuffer(contenido,dtype=np.uint8)
    imagen = cv2.imdecode(arreglo, cv2.IMREAD_COLOR)
    if imagen is None:
        raise HTTPException(status_code=400, detail="No se pudo leer la imagen.")

    rostros = analizador_facial.get(imagen)
    if len(rostros) == 0:
        raise HTTPException(
            status_code=400, 
            detail="No se detectó ningun rostro."
        )

    if len(rostros) > 1:
        raise HTTPException(
            status_code=400,
            detail="Debe aparecer una sola persona frente a la cámara.",
        )

    rostro = rostros[0]
    resultado = getattr(rostro, "liveness", None)

    if resultado is None:
        raise HTTPException(
            status_code=503,
            detail="No se pudo verificar la prueba de vida."
        )
    
    if resultado.status =="input_rejected":
        raise HTTPException(
            status_code=400,
            detail="No se pudo verificar el rostro. Centra tu cara frente a la camara"
        )

    if resultado.is_live is not True:
        raise HTTPException(
            status_code=403,
            detail="Prueba de vida no superada."
        )
    
    if rostro.normed_embedding is None:
        raise HTTPException(
            status_code=400,
            detail="No se pudo obtener el reconocimiento facial."
        )

    return np.asarray(rostro.normed_embedding, dtype=np.float32).copy()
def buscar_empleado_por_rostro(embedding_actual: np.ndarray):
    """Busca la coincidencia más cercana entre rostros de empleados activos."""
    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    e.id,
                    e.codigo,
                    e.nombres,
                    e.apellidos,
                    r.embedding
                FROM empleados e
                INNER JOIN rostros r
                    ON e.id = r.empleado_id
                WHERE e.estado = 'activo'
                """
            )
            filas = cursor.fetchall()

    finally:
        conexion.close()

    mejor_empleado = None
    mejor_similitud = -1.0
    for fila in filas:
        embedding_guardado = np.frombuffer(fila["embedding"],dtype=np.float32)
        if embedding_guardado.shape != embedding_actual.shape:
            continue
        similitud = float(np.dot(embedding_actual, embedding_guardado))
        if similitud > mejor_similitud:
            mejor_similitud = similitud
            mejor_empleado = fila

    if mejor_empleado is None or mejor_similitud < UMBRAL_SIMILITUD:
        return None, mejor_similitud
    return mejor_empleado, mejor_similitud      