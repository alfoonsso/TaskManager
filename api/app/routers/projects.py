# api/app/routers/projects.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Proyecto
from app.schemas import ProyectoResponse

# Crear el router con prefijo y etiqueta para la documentación
router = APIRouter(
            prefix='/proyectos',
            tags=['Proyectos'],
            )

@router.get('/', response_model=List[ProyectoResponse],
    summary='Listar proyectos',
    description='Devuelve la lista de proyectos con soporte de búsqueda y filtros.')

def listar_proyectos(
    skip: int = Query(0, ge=0, description='Registros a omitir'),
    limit: int = Query(20, ge=1, le=100, description='Máximo de resultados'),
    q: Optional[str] = Query(None, description='Buscar por título'),
    estado: Optional[str] = Query(None, description='Filtrar por estado'),
    db: Session = Depends(get_db)
    ):
    query = db.query(Proyecto)

    if q:
        query = query.filter(Proyecto.titulo.ilike(f'%{q}%'))
    if estado:
        query = query.filter_by(estado=estado)

    return query.order_by(Proyecto.creado_en.desc()).offset(skip).limit(limit).all()


@router.get('/{proyecto_id}', response_model=ProyectoResponse,
    summary='Obtener un proyecto',
    description='Devuelve los datos de un proyecto por su ID.')

def obtener_proyecto(
    proyecto_id: int,
    db: Session = Depends(get_db)
    ):
    proyecto = db.query(Proyecto).filter_by(id=proyecto_id).first()
    if not proyecto:
        raise HTTPException(
            status_code=404,
            detail=f'Proyecto con ID {proyecto_id} no encontrado'
            )
    return proyecto
