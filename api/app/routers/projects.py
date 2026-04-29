# api/app/routers/projects.py — versión completa y corregida
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Proyecto
from app.schemas import (
    ProyectoCreate,
    ProyectoUpdate,
    ProyectoResponse,
    RespuestaPaginada,
)

router = APIRouter(prefix='/proyectos', tags=['Proyectos'])


# ── GET /proyectos/ — Listar con filtros y paginación ────────────────
@router.get(
    '/',
    response_model=RespuestaPaginada[ProyectoResponse],
    summary='Listar proyectos',
)
def listar(
    pagina: int = Query(1, ge=1),
    tamano: int = Query(10, ge=1, le=100),
    q: Optional[str] = Query(None, description='Buscar en título y descripción'),
    estado: Optional[str] = Query(None, description='activo | pausado | completado'),
    db: Session = Depends(get_db),
):
    query = db.query(Proyecto)

    if q:
        query = query.filter(
            Proyecto.titulo.ilike(f'%{q}%')
            | Proyecto.descripcion.ilike(f'%{q}%')
        )
    if estado:
        query = query.filter(Proyecto.estado == estado)

    total = query.count()
    items = (
        query.order_by(Proyecto.creado_en.desc())
        .offset((pagina - 1) * tamano)
        .limit(tamano)
        .all()
    )

    return RespuestaPaginada(
        total=total,
        pagina=pagina,
        paginas=(total + tamano - 1) // tamano,
        items=items,
    )


# ── GET /proyectos/{id} — Detalle ────────────────────────────────────
@router.get(
    '/{proyecto_id}',
    response_model=ProyectoResponse,
    summary='Obtener un proyecto',
)
def obtener(proyecto_id: int, db: Session = Depends(get_db)):
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No existe ningún proyecto con ID {proyecto_id}',
        )
    return proyecto


# ── POST /proyectos/ — Crear ──────────────────────────────────────────
# status_code=201 porque creamos un nuevo recurso
@router.post(
    '/',
    response_model=ProyectoResponse,
    status_code=status.HTTP_201_CREATED,
    summary='Crear un proyecto',
)
def crear(datos: ProyectoCreate, db: Session = Depends(get_db)):
    # Verificar que no existe otro proyecto con el mismo título
    existente = db.query(Proyecto).filter(
        Proyecto.titulo.ilike(datos.titulo)
    ).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Ya existe un proyecto con ese título',
        )

    proyecto = Proyecto(
        titulo=datos.titulo.strip(),
        descripcion=datos.descripcion,
        fecha_limite=datos.fecha_limite,
        propietario_id=1,  # En U08 usaremos el usuario del token JWT
    )
    db.add(proyecto)
    db.commit()
    db.refresh(proyecto)  # Recargar para obtener id y creado_en asignados por la BD
    return proyecto


# ── PUT /proyectos/{id} — Actualizar completo ─────────────────────────
@router.put(
    '/{proyecto_id}',
    response_model=ProyectoResponse,
    summary='Actualizar un proyecto completo',
)
def actualizar(
    proyecto_id: int, datos: ProyectoCreate, db: Session = Depends(get_db)
):
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Proyecto no encontrado',
        )

    # PUT reemplaza todos los campos editables
    proyecto.titulo = datos.titulo.strip()
    proyecto.descripcion = datos.descripcion
    proyecto.fecha_limite = datos.fecha_limite
    db.commit()
    db.refresh(proyecto)
    return proyecto


# ── PATCH /proyectos/{id} — Actualizar parcial ────────────────────────
@router.patch(
    '/{proyecto_id}',
    response_model=ProyectoResponse,
    summary='Actualizar campos específicos de un proyecto',
)
def actualizar_parcial(
    proyecto_id: int, datos: ProyectoUpdate, db: Session = Depends(get_db)
):
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Proyecto no encontrado',
        )

    # exclude_unset=True: solo procesar los campos que el cliente envió explícitamente.
    # Si 'descripcion' no viene en el JSON, no se modifica aunque sea None en el schema.
    datos_a_actualizar = datos.model_dump(exclude_unset=True)
    for campo, valor in datos_a_actualizar.items():
        setattr(proyecto, campo, valor)

    db.commit()
    db.refresh(proyecto)
    return proyecto


# ── DELETE /proyectos/{id} — Eliminar ─────────────────────────────────
# status_code=204: éxito sin cuerpo en la respuesta
@router.delete(
    '/{proyecto_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Eliminar un proyecto',
)
def eliminar(proyecto_id: int, db: Session = Depends(get_db)):
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Proyecto no encontrado',
        )
    db.delete(proyecto)  # Cascade: elimina también las tareas del proyecto
    db.commit()
    # No devolvemos nada: 204 No Content