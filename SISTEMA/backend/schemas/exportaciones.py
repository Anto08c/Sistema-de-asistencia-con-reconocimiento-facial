from datetime import date 
from pydantic import BaseModel, model_validator

class FiltroExportacionAsistencias(BaseModel):
    fecha_desde: date
    fecha_hasta: date

    @model_validator(mode="after")
    def validar_rango_fechas(self):
        if self.fecha_desde > self.fecha_hasta:
            raise ValueError(
                "La fecha inicial no puede ser posterior a la fecha final"
            )
        return self