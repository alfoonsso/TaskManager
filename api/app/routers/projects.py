# api/app/routers/projects.py — con autenticación JWT (sección 4.2 U08)
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Proyecto, Tarea, Usuario
from app.schemas import (
    ProyectoCreate,
    ProyectoUpdate,
    ProyectoResponse,
    RespuestaPaginada,
    TareaCreate,
    TareaResponse,
)
from app.security import get_current_user

router = APIRouter(prefix='/proyectos', tags=['Proyectos'])


# ── GET /proyectos/ — PÚBLICO: sin autenticación ─────────────────────
@router.get('/',
    response_model=RespuestaPaginada[ProyectoResponse],
    summary='Listar proyectos')
def listar(
    pagina: int = Query(1, ge=1),
    tamano: int = Query(10, ge=1, le=100),
    q: Optional[str] = Query(None, description='Buscar en título y descripción'),
    estado: Optional[str] = Query(None, description='activo | pausado | completado'),
    db: Session = Depends(get_db)
):
    query = db.query(Proyecto)
    if q:
        query = query.filter(
            Proyecto.titulo.ilike(f'%{q}%') |
            Proyecto.descripcion.ilike(f'%{q}%')
        )
    if estado:
        query = query.filter(Proyecto.estado == estado)
    total = query.count()
    items = (query.order_by(Proyecto.creado_en.desc())
                  .offset((pagina - 1) * tamano)
                  .limit(tamano)
                  .all())
    return RespuestaPaginada(
        total=total,
        pagina=pagina,
        paginas=(total + tamano - 1) // tamano,
        items=items
    )


# ── GET /proyectos/{id} — PÚBLICO: sin autenticación ─────────────────
@router.get('/{proyecto_id}',
    response_model=ProyectoResponse,
    summary='Obtener un proyecto')
def obtener(proyecto_id: int, db: Session = Depends(get_db)):
    proyecto = db.query(Proyecto).filter_by(id=proyecto_id).first()
    if not proyecto:
        raise HTTPException(status_code=404,
            detail=f'No existe ningún proyecto con ID {proyecto_id}')
    return proyecto


# ── POST /proyectos/ — AUTENTICADO: requiere token ────────────────────
@router.post('/',
    response_model=ProyectoResponse,
    status_code=status.HTTP_201_CREATED,
    summary='Crear un proyecto')
def crear(
    datos: ProyectoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)    # ← Token requerido
):
    existente = db.query(Proyecto).filter(
        Proyecto.titulo.ilike(datos.titulo)).first()
    if existente:
        raise HTTPException(status_code=409,
            detail='Ya existe un proyecto con ese título')
    proyecto = Proyecto(
        titulo         = datos.titulo.strip(),
        descripcion    = datos.descripcion,
        fecha_limite   = datos.fecha_limite,
        propietario_id = usuario.id     # ← ID del token, no hardcodeado
    )
    db.add(proyecto)
    db.commit()
    db.refresh(proyecto)
    return proyecto


# ── PUT /proyectos/{id} — AUTENTICADO + PROPIETARIO O ADMIN ──────────
@router.put('/{proyecto_id}',
    response_model=ProyectoResponse,
    summary='Actualizar un proyecto completo')
def actualizar(
    proyecto_id: int,
    datos: ProyectoCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    proyecto = db.query(Proyecto).filter_by(id=proyecto_id).first()
    if not proyecto:
        raise HTTPException(status_code=404, detail='Proyecto no encontrado')
    # Solo el propietario o un admin puede editar
    if proyecto.propietario_id != usuario.id and not usuario.es_admin:
        raise HTTPException(status_code=403,
            detail='No tienes permiso para editar este proyecto')
    proyecto.titulo       = datos.titulo.strip()
    proyecto.descripcion  = datos.descripcion
    proyecto.fecha_limite = datos.fecha_limite
    db.commit()
    db.refresh(proyecto)
    return proyecto


# ── PATCH /proyectos/{id} — AUTENTICADO + PROPIETARIO O ADMIN ────────
@router.patch('/{proyecto_id}',
    response_model=ProyectoResponse,
    summary='Actualizar campos específicos de un proyecto')
def actualizar_parcial(
    proyecto_id: int,
    datos: ProyectoUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    proyecto = db.query(Proyecto).filter_by(id=proyecto_id).first()
    if not proyecto:
        raise HTTPException(status_code=404, detail='Proyecto no encontrado')
    if proyecto.propietario_id != usuario.id and not usuario.es_admin:
        raise HTTPException(status_code=403,
            detail='No tienes permiso para editar este proyecto')
    datos_a_actualizar = datos.model_dump(exclude_unset=True)
    for campo, valor in datos_a_actualizar.items():
        setattr(proyecto, campo, valor)
    db.commit()
    db.refresh(proyecto)
    return proyecto


# ── DELETE /proyectos/{id} — AUTENTICADO + PROPIETARIO O ADMIN ───────
@router.delete('/{proyecto_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Eliminar un proyecto')
def eliminar(
    proyecto_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)
):
    proyecto = db.query(Proyecto).filter_by(id=proyecto_id).first()
    if not proyecto:
        raise HTTPException(status_code=404, detail='Proyecto no encontrado')
    if proyecto.propietario_id != usuario.id and not usuario.es_admin:
        raise HTTPException(status_code=403,
            detail='No tienes permiso para eliminar este proyecto')
    db.delete(proyecto)     # Cascade: elimina también las tareas del proyecto
    db.commit()
    # No devolvemos nada: 204 No Content


# ═══════════════════════════════════════════════════════════════════════
# RECURSOS ANIDADOS — sección 4.1 U07
# ═══════════════════════════════════════════════════════════════════════

# ── GET /proyectos/{id}/tareas — PÚBLICO ─────────────────────────────
@router.get('/{proyecto_id}/tareas',
    response_model=List[TareaResponse],
    tags=['Proyectos', 'Tareas'],
    summary='Tareas de un proyecto')
def tareas_del_proyecto(
    proyecto_id: int,
    estado: Optional[str] = Query(None),
    prioridad: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    proyecto = db.query(Proyecto).filter_by(id=proyecto_id).first()
    if not proyecto:
        raise HTTPException(404, 'Proyecto no encontrado')
    query = db.query(Tarea).filter_by(proyecto_id=proyecto_id)
    if estado:
        query = query.filter_by(estado=estado)
    if prioridad:
        query = query.filter_by(prioridad=prioridad)
    return query.order_by(Tarea.creado_en.desc()).all()


# ── POST /proyectos/{id}/tareas — AUTENTICADO ────────────────────────
@router.post('/{proyecto_id}/tareas',
    response_model=TareaResponse,
    status_code=status.HTTP_201_CREATED,
    tags=['Proyectos', 'Tareas'],
    summary='Crear tarea en un proyecto')
def crear_tarea_en_proyecto(
    proyecto_id: int,
    datos: TareaCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user)    # ← Token requerido
):
    proyecto = db.query(Proyecto).filter_by(id=proyecto_id).first()
    if not proyecto:
        raise HTTPException(404, 'Proyecto no encontrado')
    tarea_data = datos.model_dump()
    tarea_data['proyecto_id'] = proyecto_id     # Sobrescribir con el de la URL
    tarea = Tarea(**tarea_data)
    db.add(tarea)
    db.commit()
    db.refresh(tarea)
    return tarea