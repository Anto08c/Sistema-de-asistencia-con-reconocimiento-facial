from fastapi import APIRouter, HTTPException
import pymysql

from backend.conexion import obtener_conexion
from backend.empleados import listar_empleados, registrar_empleado, cambiar_estado_empleado
from backend.schemas.empleados import EmpleadoNuevo, CambioEstado, EmpleadoConRostro
from backend.services.reconocimiento_facial import obtener_embedding_de_imagen

router = APIRouter(tags=["Empleados"])


@router.get("/empleados")
def obtener_empleados():
    return listar_empleados()


@router.post("/empleados")
def crear_empleado(datos: EmpleadoNuevo):
    correcto, mensaje = registrar_empleado(datos.codigo, datos.nombres, datos.apellidos)
    return {"ok": correcto, "mensaje": mensaje}


@router.patch("/empleados/{empleado_id}/estado")
def actualizar_estado(empleado_id: int, datos: CambioEstado):
    correcto, mensaje = cambiar_estado_empleado(empleado_id, datos.estado)
    return {"ok": correcto, "mensaje": mensaje}


@router.post("/empleados/con-rostro")
def registrar_empleado_con_rostro(datos: EmpleadoConRostro):
    codigo = datos.codigo.strip().upper()
    nombres = datos.nombres.strip()
    apellidos = datos.apellidos.strip()
    if not codigo or not nombres or not apellidos:
        raise HTTPException(status_code=400, detail="Todos los campos son obligatorios.")

    embedding = obtener_embedding_de_imagen(datos.imagen)
    conexion = obtener_conexion()
    try:
        conexion.begin()
        with conexion.cursor() as cursor:
            cursor.execute(
                "INSERT INTO empleados (codigo, nombres, apellidos, estado) VALUES (%s, %s, %s, 'activo')",
                (codigo, nombres, apellidos),
            )
            empleado_id = cursor.lastrowid
            cursor.execute(
                "INSERT INTO rostros (empleado_id, embedding) VALUES (%s, %s)",
                (empleado_id, embedding.tobytes()),
            )
        conexion.commit()
        return {"ok": True, "mensaje": "Empleado y rostro registrados correctamente.", "empleado_id": empleado_id}
    except pymysql.err.IntegrityError as error:
        conexion.rollback()
        raise HTTPException(status_code=409, detail="El código del empleado ya existe.") from error
    except Exception as error:
        conexion.rollback()
        print("Error al registrar empleado y rostro:", error)
        raise HTTPException(status_code=500, detail="No se pudo registrar el empleado y su rostro.") from error
    finally:
        conexion.close()
