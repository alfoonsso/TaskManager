# api/app/routers/tasks.py — con autenticación JWT (sección 5.1 U08)
from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Tarea, Proyecto, Usuario
from app.schemas import TareaCreate, TareaUpdate, TareaResponse
from app.security import get_current_user

router = APIRouter(prefix='/tareas', tags=['Tareas'])

ESTADOS_VALIDOS     = ['pendiente', 'en_progreso', 'revision', 'completada']
PRIORIDADES_VALIDAS = ['baja', 'media', 'alta', 'urgente']


# ── GET /tareas/ — PÚBLICO ───────────────────────────────────────────
@router.get('/', response_model=List[TareaResponse])
def listar(
    proyecto_id: Optional[int] = Query(None),
    prioridad:   Optional[str] = Query(None),
    estado:      Optional[str] = Query(None),
    asignado_id: Optional[int] = Query(None),
    skip:  int = Query(0,  ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    query = db.query(Tarea)
    if proyecto_id:
        query = query.filter_by(proyecto_id=proyecto_id)
    if prioridad:
        if prioridad not in PRIORIDADES_VALIDAS:
            raise HTTPException(400, f'Prioridad no válida. Usa: {PRIORIDADES_VALIDAS}')
        query = query.filter_by(prioridad=prioridad)
    if estado:
        if estado not in ESTADOS_VALIDOS:
            raise HTTPException(400, f'Estado no válido. Usa: {ESTADOS_VALIDOS}')
        query = query.filter_by(estado=estado)
    if asignado_id:
        query = query.filter_by(asignado_id=asignado_id)
    return query.offset(skip).limit(limit).all()


# ── GET /tareas/{id} — PÚBLICO ───────────────────────────────────────
@router.get('/{tarea_id}', response_model=TareaResponse)
def obtener(tarea_id: int, db: Session = Depends(get_db)):
    tarea = db.query(Tarea).filter_by(id=tarea_id).first()
    if not tarea:
        raise HTTPException(404, 'Tarea no encontrada')
    return tarea


# ── POST /tareas/ — AUTENTICADO ──────────────────────────────────────
@router.post('/', response_model=TareaResponse,
             status_code=status.HTTP_201_CREATED)
def crear(
    datos: TareaCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)    # ← Token requerido
):
    proyecto = db.query(Proyecto).filter_by(id=datos.proyecto_id).first()
    if not proyecto:
        raise HTTPException(404, f'No existe el proyecto con ID {datos.proyecto_id}')
    tarea = Tarea(**datos.model_dump())
    db.add(tarea)
    db.commit()
    db.refresh(tarea)
    return tarea


# ── PATCH /tareas/{id}/estado — AUTENTICADO ──────────────────────────
# Declarado ANTES de /{tarea_id} para que FastAPI no interprete
# 'estado' como un tarea_id entero.
@router.patch('/{tarea_id}/estado', response_model=TareaResponse,
              summary='Cambiar el estado de una tarea',
              description='Cambia solo el estado de una tarea validando la transición.')
def cambiar_estado(
    tarea_id: int,
    nuevo_estado: str = Body(..., embed=True,
                             description='Nuevo estado de la tarea'),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)    # ← Token requerido
):
    if nuevo_estado not in ESTADOS_VALIDOS:
        raise HTTPException(400, detail={
            'mensaje': 'Estado no válido',
            'estados_validos': ESTADOS_VALIDOS
        })
    tarea = db.query(Tarea).filter_by(id=tarea_id).first()
    if not tarea:
        raise HTTPException(404, 'Tarea no encontrada')
    tarea.estado = nuevo_estado
    db.commit()
    db.refresh(tarea)
    return tarea


# ── PATCH /tareas/{id} — PROPIETARIO DEL PROYECTO O ADMIN ────────────
@router.patch('/{tarea_id}', response_model=TareaResponse)
def actualizar(
    tarea_id: int,
    datos: TareaUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    tarea = db.query(Tarea).filter_by(id=tarea_id).first()
    if not tarea:
        raise HTTPException(404, 'Tarea no encontrada')

    # Verificar: asignado a la tarea, propietario del proyecto, o admin
    proyecto       = db.query(Proyecto).filter_by(id=tarea.proyecto_id).first()
    es_asignado    = tarea.asignado_id == usuario.id
    es_propietario = proyecto and proyecto.propietario_id == usuario.id
    if not es_asignado and not es_propietario and not usuario.es_admin:
        raise HTTPException(403, 'No tienes permiso para editar esta tarea')

    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(tarea, campo, valor)
    db.commit()
    db.refresh(tarea)
    return tarea


# ── DELETE /tareas/{id} — PROPIETARIO DEL PROYECTO O ADMIN ───────────
@router.delete('/{tarea_id}', status_code=status.HTTP_204_NO_CONTENT)
def eliminar(
    tarea_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    tarea = db.query(Tarea).filter_by(id=tarea_id).first()
    if not tarea:
        raise HTTPException(404, 'Tarea no encontrada')

    # Solo el propietario del proyecto o un admin puede eliminar tareas
    proyecto       = db.query(Proyecto).filter_by(id=tarea.proyecto_id).first()
    es_propietario = proyecto and proyecto.propietario_id == usuario.id
    if not es_propietario and not usuario.es_admin:
        raise HTTPException(403, 'No tienes permiso para eliminar esta tarea')

    db.delete(tarea)
    db.commit()
    # No devolvemos nada: 204 No Content