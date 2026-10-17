from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

import sqlite3
import base64
import cv2
import numpy as np

from insightface.app import FaceAnalysis
from fastapi import HTTPException
from backend.asistencia import (
    registrar_asistencia,
    cargar_rostros_registrados,
    listar_asistencias
)


# Modelo facial: se carga una vez al iniciar el servidor
analizador_facial = FaceAnalysis(
    name="buffalo_l",
    providers=["CPUExecutionProvider"]
)

analizador_facial.prepare(
    ctx_id=0,
    det_size=(640, 640)
)

UMBRAL_SIMILITUD = 0.45


from backend.empleados import (
    listar_empleados,
    registrar_empleado,
    cambiar_estado_empleado,
)

app = FastAPI(
    title="Sistema de Asistencia Facial",
    description="API del sistema de asistencia",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


RUTA_FRONTEND = (
    Path(__file__).resolve().parent.parent
    / "frontend"
    / "index.html"
)


class EmpleadoNuevo(BaseModel):
    codigo: str
    nombres: str
    apellidos: str


class CambioEstado(BaseModel):
    estado: str


class MarcacionFacial(BaseModel):
    imagen: str
    tipo: str

class EmpleadoConRostro(BaseModel):
    codigo: str
    nombres: str
    apellidos: str
    imagen: str

@app.get("/")
def inicio():
    return {"mensaje": "Sistema de Asistencia Facial funcionando"}


@app.get("/panel", include_in_schema=False)
def mostrar_panel():
    return FileResponse(RUTA_FRONTEND)


@app.get("/empleados")
def obtener_empleados():
    return listar_empleados()


@app.post("/empleados")
def crear_empleado(datos: EmpleadoNuevo):
    correcto, mensaje = registrar_empleado(
        datos.codigo,
        datos.nombres,
        datos.apellidos,
    )
    return {"ok": correcto, "mensaje": mensaje}


@app.patch("/empleados/{empleado_id}/estado")
def actualizar_estado(empleado_id: int, datos: CambioEstado):
    correcto, mensaje = cambiar_estado_empleado(
        empleado_id,
        datos.estado,
    )
    return {"ok": correcto, "mensaje": mensaje}


@app.get("/asistencias")
def obtener_asistencias():
    return listar_asistencias()


@app.post("/asistencia/facial")
def marcar_asistencia_facial(datos: MarcacionFacial):
    if datos.tipo not in ("entrada", "salida"):
        raise HTTPException(
            status_code=400,
            detail="El tipo debe ser entrada o salida."
        )

    try:
        imagen_base64 = datos.imagen.split(",")[-1]
        contenido = base64.b64decode(imagen_base64, validate=True)
        arreglo = np.frombuffer(contenido, dtype=np.uint8)
        imagen = cv2.imdecode(arreglo, cv2.IMREAD_COLOR)

        if imagen is None:
            raise HTTPException(
                status_code=400,
                detail="No se pudo leer la imagen."
            )

        rostros_detectados = analizador_facial.get(imagen)

        if len(rostros_detectados) == 0:
            return {"ok": False, "mensaje": "No se detectó ningún rostro."}

        if len(rostros_detectados) > 1:
            return {
                "ok": False,
                "mensaje": "Debe aparecer una sola persona frente a la cámara."
            }

        rostro = rostros_detectados[0]
        embedding_actual = rostro.embedding.astype(np.float32)
        ruta_bd = Path(__file__).resolve().parent.parent / "datos" / "asistencia.db"

        with sqlite3.connect(ruta_bd) as conexion:
            filas = conexion.execute("""
                SELECT e.id, e.codigo, e.nombres, e.apellidos, r.embedding
                FROM empleados e
                JOIN rostros r ON r.empleado_id = e.id
                WHERE e.estado = 'activo'
            """).fetchall()

        if not filas:
            return {
                "ok": False,
                "mensaje": "No hay empleados activos con rostro registrado."
            }

        mejor_empleado = None
        mejor_similitud = -1.0

        for empleado_id, codigo, nombres, apellidos, embedding_bytes in filas:
            embedding_guardado = np.frombuffer(
                embedding_bytes, dtype=np.float32
            )

            if embedding_guardado.shape != embedding_actual.shape:
                continue

            denominador = (
                np.linalg.norm(embedding_actual)
                * np.linalg.norm(embedding_guardado)
            )

            if denominador == 0:
                continue

            similitud = float(
                np.dot(embedding_actual, embedding_guardado) / denominador
            )

            if similitud > mejor_similitud:
                mejor_similitud = similitud
                mejor_empleado = (
                    empleado_id, codigo, nombres, apellidos
                )

        if mejor_empleado is None or mejor_similitud < UMBRAL_SIMILITUD:
            return {
                "ok": False,
                "mensaje": "Rostro no reconocido."
            }

        empleado_id, codigo, nombres, apellidos = mejor_empleado

        resultado = registrar_asistencia(empleado_id, datos.tipo)

        if isinstance(resultado, dict):
            if not resultado.get("ok", True):
                return resultado
            mensaje = resultado.get("mensaje", "Asistencia registrada.")
        else:
            mensaje = str(resultado or "Asistencia registrada.")

        return {
            "ok": True,
            "mensaje": mensaje,
            "empleado": f"{nombres} {apellidos}",
            "codigo": codigo,
            "tipo": datos.tipo,
            "similitud": round(mejor_similitud, 3)
        }

    except HTTPException:
       raise
    except Exception as error:
        print("Error en marcación facial:", error)
        raise HTTPException(
            status_code=500,
            detail="Ocurrió un error al procesar la marcación."
        )
    
@app.post("/empleados/con-rostro")
def registrar_empleado_con_rostro(datos: EmpleadoConRostro):
    try:
        # Decodificar imagen enviada por el navegador
        imagen_base64 = datos.imagen.split(",")[-1]
        contenido = base64.b64decode(imagen_base64, validate=True)
        arreglo = np.frombuffer(contenido, dtype=np.uint8)
        imagen = cv2.imdecode(arreglo, cv2.IMREAD_COLOR)

        if imagen is None:
            raise HTTPException(400, "No se pudo leer la imagen.")

        # Detectar el rostro
        rostros = analizador_facial.get(imagen)

        if len(rostros) == 0:
            raise HTTPException(400, "No se detectó ningún rostro.")

        if len(rostros) > 1:
            raise HTTPException(
                400, "Debe aparecer una sola persona en la cámara."
            )

        embedding = rostros[0].embedding.astype(np.float32)

        ruta_bd = (
            Path(__file__).resolve().parent.parent
            / "datos" / "asistencia.db"
        )

        with sqlite3.connect(ruta_bd) as conexion:
            cursor = conexion.execute(
                """
                INSERT INTO empleados
                    (codigo, nombres, apellidos, estado)
                VALUES (?, ?, ?, 'activo')
                """,
                (
                    datos.codigo.strip(),
                    datos.nombres.strip(),
                    datos.apellidos.strip()
                )
            )

            empleado_id = cursor.lastrowid

            conexion.execute(
                """
                INSERT INTO rostros (empleado_id, embedding)
                VALUES (?, ?)
                """,
                (empleado_id, embedding.tobytes())
            )

        return {
            "ok": True,
            "mensaje": "Empleado y rostro registrados correctamente.",
            "empleado_id": empleado_id
        }

    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="El código del empleado ya existe."
        )
    except HTTPException:
        raise
    except Exception as error:
        print("Error al registrar empleado y rostro:", error)
        raise HTTPException(
            status_code=500,
            detail="No se pudo completar el registro."
        )

    