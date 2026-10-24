from fastapi import APIRouter, Query, HTTPException 
from backend.exportaciones import generar_csv_asistencias
from datetime import date 
from fastapi.responses import StreamingResponse
import io
router = APIRouter(tags=["Exportaciones"])


@router.get("/exportar/asistencias")
def exportar_asistencias(
    fecha_desde: date = Query(...),
    fecha_hasta: date = Query(...)
    ):

    if fecha_desde > fecha_hasta:
        raise HTTPException(
            status_code=400,
            detail="La fecha inicial no puede ser posterior a la fecha final."
        )

    try:
        contenido = generar_csv_asistencias(
            fecha_desde,
            fecha_hasta
        )

        nombre_archivo = (
            f"asistencias_{fecha_desde}_{fecha_hasta}.csv"
        )

        return StreamingResponse(
            io.BytesIO(contenido),
            media_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition":
                    f'attachment; filename="{nombre_archivo}"'
            }
        )

    except HTTPException:
        raise

    except Exception as error:
        print("Error al exportar asistencias:", error)

        raise HTTPException(
            status_code=500,
            detail="No se pudo generar el reporte de asistencias."
        )
