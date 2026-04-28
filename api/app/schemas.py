# api/app/schemas.py
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime, date


# ═══════════════════════════════════════════════════
# PROYECTO
# ═══════════════════════════════════════════════════

class ProyectoBase(BaseModel):
    """Campos comunes a todos los schemas de Proyecto."""
    titulo: str = Field(..., min_length=3, max_length=100,
                        description='Título del proyecto')
    descripcion: Optional[str] = Field(None, max_length=500)
    fecha_limite: Optional[date] = None

class ProyectoCreate(ProyectoBase):
    """Schema para crear un proyecto. Hereda de ProyectoBase sin añadir nada."""
    pass

class ProyectoUpdate(BaseModel):
    """Schema para actualizar un proyecto. Todos los campos son opcionales."""
    titulo: Optional[str] = Field(None, min_length=3, max_length=100)
    descripcion: Optional[str] = None
    estado: Optional[str] = None
    fecha_limite: Optional[date] = None

class ProyectoResponse(ProyectoBase):
    """Schema para la respuesta. Incluye campos generados por el servidor."""
    id: int
    estado: str
    creado_en: datetime
    propietario_id: int
    progreso: int = 0 # Calculado, no almacenado en la BD

class Config:
    # from_attributes=True permite crear el schema desde objetos SQLAlchemy
    # (antes se llamaba orm_mode=True en Pydantic v1)
    from_attributes = True


# ═══════════════════════════════════════════════════
# TAREA
# ═══════════════════════════════════════════════════
class TareaBase(BaseModel):
    titulo: str = Field(..., min_length=3, max_length=200)
    descripcion: Optional[str] = None
    prioridad: str = Field('media',
    pattern='^(baja|media|alta|urgente)$')
    estado: str = Field('pendiente',
                        pattern='^(pendiente|en_progreso|revision|completada)$')
    fecha_limite: Optional[date] = None

class TareaCreate(TareaBase):
    proyecto_id: int
    asignado_id: Optional[int] = None

class TareaUpdate(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    prioridad: Optional[str] = None
    estado: Optional[str] = None
    asignado_id: Optional[int] = None
    fecha_limite: Optional[date] = None

class TareaResponse(TareaBase):
    id: int
    proyecto_id: int
    asignado_id: Optional[int]
    creado_en: datetime

class Config:
    from_attributes = True


# ═══════════════════════════════════════════════════
# USUARIO
# ═══════════════════════════════════════════════════

class UsuarioCreate(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    email: EmailStr # Valida formato email automáticamente
    password: str = Field(..., min_length=8)

class UsuarioResponse(BaseModel):
    """Nunca incluir la contraseña en la respuesta."""
    id: int
    nombre: str
    email: str
    rol: str
    creado_en: datetime

class Config:
    from_attributes = True


# ═══════════════════════════════════════════════════
# RESPUESTA PAGINADA (genérica)
# ═══════════════════════════════════════════════════

from typing import TypeVar, Generic
T = TypeVar('T')

class RespuestaPaginada(BaseModel, Generic[T]):
    total: int
    pagina: int
    paginas: int
    items: List[T]
