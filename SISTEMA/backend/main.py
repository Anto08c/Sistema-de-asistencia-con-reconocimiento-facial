from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from backend.routers.empleados import router as empleados_router
from backend.routers.asistencias import router as asistencias_router
from backend.routers.exportaciones import router as exportaciones_router

RUTA_FRONTEND = Path(__file__).resolve().parent.parent / "frontend" / "index.html"

app = FastAPI(
    title="Sistema de Asistencia Facial",
    description="API del sistema de asistencia",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200", "*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(empleados_router)
app.include_router(asistencias_router)
app.include_router(exportaciones_router)


@app.get("/")
def inicio():
    return {"mensaje": "Sistema de Asistencia Facial funcionando"}


@app.get("/panel", include_in_schema=False)
def mostrar_panel():
    return FileResponse(RUTA_FRONTEND)