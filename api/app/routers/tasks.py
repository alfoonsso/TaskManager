# api/app/routers/tasks.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Tarea, Proyecto
from app.schemas import TareaResponse

router = APIRouter(prefix='/tareas', tags=['Tareas'])

@router.get('/', response_model=List[TareaResponse],
    summary='Listar tareas')

def listar_tareas(
    proyecto_id: Optional[int] = Query(None, description='Filtrar por proyecto'),
    prioridad: Optional[str] = Query(None, description='Filtrar por prioridad'),
    estado: Optional[str] = Query(None, description='Filtrar por estado'),
    asignado_id: Optional[int] = Query(None, description='Filtrar por asignado'),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
    ):
    query = db.query(Tarea)

    if proyecto_id: query = query.filter_by(proyecto_id=proyecto_id)
    if prioridad: query = query.filter_by(prioridad=prioridad)
    if estado: query = query.filter_by(estado=estado)
    if asignado_id: query = query.filter_by(asignado_id=asignado_id)

    return query.offset(skip).limit(limit).all()


@router.get('/{tarea_id}', response_model=TareaResponse)
def obtener_tarea(tarea_id: int, db: Session = Depends(get_db)):
    tarea = db.query(Tarea).filter_by(id=tarea_id).first()
    if not tarea:
        raise HTTPException(status_code=404, detail='Tarea no encontrada')
    return tarea


# Endpoint para obtener todas las tareas de un proyecto específico
@router.get('/proyecto/{proyecto_id}', response_model=List[TareaResponse],
summary='Tareas de un proyecto')

def tareas_de_proyecto(proyecto_id: int, db: Session = Depends(get_db)):
    proyecto = db.query(Proyecto).filter_by(id=proyecto_id).first()
    if not proyecto:
        raise HTTPException(status_code=404, detail='Proyecto no encontrado')
    return db.query(Tarea).filter_by(proyecto_id=proyecto_id).all()