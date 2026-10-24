from pydantic import BaseModel 

class MarcacionFacial(BaseModel):
    imagen: str
    tipo: str