"""Objetos de entrada de la API (solo Pydantic, sin FastAPI) para poder probarlos sin levantar el servidor.

Los límites de longitud son más amplios que los del formulario del Portal Ciudadano
(título 120 y descripción 1500 caracteres): ningún reclamo enviado desde la web se rechaza,
pero el servidor ya no acepta textos de cualquier tamaño de clientes externos.
"""
from typing import Optional

from pydantic import BaseModel, Field

MAX_TITULO = 200
MAX_DESCRIPCION = 2000
MAX_UBICACION = 300
MAX_DATO_PERSONAL = 200


class ReclamoDTO(BaseModel):
    titulo: str = Field(min_length=1, max_length=MAX_TITULO)
    descripcion: str = Field(min_length=1, max_length=MAX_DESCRIPCION)
    categoria: Optional[str] = Field(default=None, max_length=50)  # Puede venir nulo desde React
    ubicacion: Optional[str] = Field(default="", max_length=MAX_UBICACION)
    # Datos personales: se enmascaran en el backend y nunca se envían a Gemini
    dni: Optional[str] = Field(default="", max_length=20)
    nombre: Optional[str] = Field(default="", max_length=MAX_DATO_PERSONAL)
    direccion: Optional[str] = Field(default="", max_length=MAX_DATO_PERSONAL)
    contacto: Optional[str] = Field(default="", max_length=MAX_DATO_PERSONAL)


class EstadoDTO(BaseModel):
    estado: str = Field(min_length=1, max_length=20)
