# api/app/routers/tasks.py — versión completa
from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Tarea, Proyecto
from app.schemas import TareaCreate, TareaUpdate, TareaResponse

router = APIRouter(prefix='/tareas', tags=['Tareas'])

ESTADOS_VALIDOS = ['pendiente', 'en_progreso', 'revision', 'completada']
PRIORIDADES_VALIDAS = ['baja', 'media', 'alta', 'urgente']


# ── GET /tareas/ — Listar con filtros ────────────────────────────────
@router.get('/', response_model=List[TareaResponse])
def listar(
    proyecto_id: Optional[int] = Query(None),
    prioridad: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    asignado_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    query = db.query(Tarea)
    if proyecto_id:
        query = query.filter_by(proyecto_id=proyecto_id)
    if prioridad:
        if prioridad not in PRIORIDADES_VALIDAS:
            raise HTTPException(400,
                f'Prioridad no válida. Usa: {PRIORIDADES_VALIDAS}')
        query = query.filter_by(prioridad=prioridad)
    if estado:
        if estado not in ESTADOS_VALIDOS:
            raise HTTPException(400,
                f'Estado no válido. Usa: {ESTADOS_VALIDOS}')
        query = query.filter_by(estado=estado)
    if asignado_id:
        query = query.filter_by(asignado_id=asignado_id)
    return query.offset(skip).limit(limit).all()


# ── GET /tareas/{id} ─────────────────────────────────────────────────
@router.get('/{tarea_id}', response_model=TareaResponse)
def obtener(tarea_id: int, db: Session = Depends(get_db)):
    tarea = db.query(Tarea).filter_by(id=tarea_id).first()
    if not tarea:
        raise HTTPException(404, 'Tarea no encontrada')
    return tarea


# ── POST /tareas/ — Crear ────────────────────────────────────────────
@router.post('/', response_model=TareaResponse,
             status_code=status.HTTP_201_CREATED)
def crear(datos: TareaCreate, db: Session = Depends(get_db)):
    # Verificar que el proyecto existe
    proyecto = db.query(Proyecto).filter_by(id=datos.proyecto_id).first()
    if not proyecto:
        raise HTTPException(404,
            f'No existe el proyecto con ID {datos.proyecto_id}')
    tarea = Tarea(**datos.model_dump())
    db.add(tarea)
    db.commit()
    db.refresh(tarea)
    return tarea


# ── PATCH /tareas/{id} — Actualizar parcial ──────────────────────────
@router.patch('/{tarea_id}', response_model=TareaResponse)
def actualizar(tarea_id: int, datos: TareaUpdate,
               db: Session = Depends(get_db)):
    tarea = db.query(Tarea).filter_by(id=tarea_id).first()
    if not tarea:
        raise HTTPException(404, 'Tarea no encontrada')
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(tarea, campo, valor)
    db.commit()
    db.refresh(tarea)
    return tarea


# ── PATCH /tareas/{id}/estado — Cambio de estado ─────────────────────
# IMPORTANTE: este endpoint debe declararse ANTES de /{tarea_id}
# para que FastAPI no interprete 'estado' como un tarea_id entero.
@router.patch('/{tarea_id}/estado', response_model=TareaResponse,
              summary='Cambiar el estado de una tarea',
              description='Cambia solo el estado de una tarea validando la transición.')
def cambiar_estado(
    tarea_id: int,
    nuevo_estado: str = Body(..., embed=True,
                             description='Nuevo estado de la tarea'),
    db: Session = Depends(get_db)
):
    # embed=True → el JSON debe tener la forma: {"nuevo_estado": "completada"}
    if nuevo_estado not in ESTADOS_VALIDOS:
        raise HTTPException(400,
            detail={
                'mensaje': 'Estado no válido',
                'estados_validos': ESTADOS_VALIDOS
            }
        )
    tarea = db.query(Tarea).filter_by(id=tarea_id).first()
    if not tarea:
        raise HTTPException(404, 'Tarea no encontrada')
    tarea.estado = nuevo_estado
    db.commit()
    db.refresh(tarea)
    return tarea


# ── DELETE /tareas/{id} ───────────────────────────────────────────────
@router.delete('/{tarea_id}', status_code=status.HTTP_204_NO_CONTENT)
def eliminar(tarea_id: int, db: Session = Depends(get_db)):
    tarea = db.query(Tarea).filter_by(id=tarea_id).first()
    if not tarea:
        raise HTTPException(404, 'Tarea no encontrada')
    db.delete(tarea)
    db.commit()
    # No devolvemos nada: 204 No Content