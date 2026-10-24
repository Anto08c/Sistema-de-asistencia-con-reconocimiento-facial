from pydantic import BaseModel


class EmpleadoNuevo(BaseModel):
    codigo: str
    nombres: str
    apellidos: str


class CambioEstado(BaseModel):
    estado: str


class EmpleadoConRostro(BaseModel):
    codigo: str
    nombres: str
    apellidos: str
    imagen: str
