from fastapi import APIRouter, HTTPException

from backend.asistencia import registrar_asistencia, listar_asistencias
from backend.schemas.asistencias import MarcacionFacial
from backend.services.reconocimiento_facial import (
    obtener_embedding_de_imagen,
    buscar_empleado_por_rostro,
)

router = APIRouter(tags=["Asistencias"])


@router.get("/asistencias")
def obtener_asistencias():
    return listar_asistencias()


@router.post("/asistencia/facial")
def marcar_asistencia_facial(datos: MarcacionFacial):
    if datos.tipo not in ("entrada", "salida"):
        raise HTTPException(status_code=400, detail="El tipo debe ser entrada o salida.")
    try:
        embedding = obtener_embedding_de_imagen(datos.imagen)
        empleado, similitud = buscar_empleado_por_rostro(embedding)
        if empleado is None:
            return {"ok": False, "mensaje": "Rostro no reconocido."}

        correcto, mensaje = registrar_asistencia(empleado["id"], datos.tipo)
        return {
            "ok": correcto,
            "mensaje": mensaje,
            "empleado": empleado["nombres"] + " " + empleado["apellidos"],
            "codigo": empleado["codigo"],
            "tipo": datos.tipo,
            "similitud": round(similitud, 3),
        }
    except HTTPException:
        raise
    except Exception as error:
        print("Error en marcación facial:", error)
        raise HTTPException(status_code=500, detail="Ocurrió un error al procesar la marcación.") from error
