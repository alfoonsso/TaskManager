from flask import Blueprint, render_template, abort, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app.forms import ProyectoForm, BusquedaForm, FormularioVacio
from app import db
from app.models import Proyecto, Tarea
# url_prefix='/proyectos' hace que TODAS las rutas de este Blueprint
# tengan /proyectos como prefijo automáticamente.
projects = Blueprint('projects', __name__, url_prefix='/proyectos')

@projects.route('/')
@login_required
def lista():
    q = request.args.get('q', '').strip()
    pagina = request.args.get('pagina', 1, type=int)
    
    if current_user.es_admin:
        query = Proyecto.query.order_by(Proyecto.creado_en.desc())
    else:
        query = Proyecto.query.filter_by(propietario_id=current_user.id)\
                              .order_by(Proyecto.creado_en.desc())

    if q:
        query = query.filter(
            db.or_(Proyecto.titulo.ilike(f'%{q}%'),
                   Proyecto.descripcion.ilike(f'%{q}%'))
        )
        
    paginacion = query.paginate(page=pagina, per_page=10, error_out=False)    
    return render_template('projects/lista.html',
                            proyectos=paginacion.items,                                
                            paginacion=paginacion,
                            q=q,
                            form_busqueda=BusquedaForm())

@projects.route('/<int:pid>')
@login_required # ← Protege esta ruta
def detalle(pid):
    proyecto = Proyecto.query.get_or_404(pid)
    tareas = proyecto.tareas.order_by(Tarea.creado_en.desc()).all()
    return render_template('projects/detalle.html',
                            proyecto=proyecto,
                            tareas=tareas,
                            form=FormularioVacio())

@projects.route('/nuevo', methods=['GET', 'POST'])
@login_required # ← Protege esta ruta
def nuevo():
    form = ProyectoForm()
    if form.validate_on_submit():
        proyecto = Proyecto(
                    titulo = form.titulo.data,
                    descripcion = form.descripcion.data,
                    fecha_limite = form.fecha_limite.data,
                    propietario_id = current_user.id # En U05 usaremos current_user.id
                    )
        db.session.add(proyecto)
        db.session.commit()
        flash(f'Proyecto "{proyecto.titulo}" creado.', 'success')
        return redirect(url_for('projects.lista'))
    
    return render_template('projects/form.html',
                            form=form, titulo_pagina='Nuevo proyecto')

@projects.route('/<int:pid>/editar', methods=['GET', 'POST'])
@login_required
def editar(pid):
    proyecto = Proyecto.query.get_or_404(pid)
    if proyecto.propietario_id != current_user.id and not current_user.es_admin:
        abort(403)
    form = ProyectoForm(obj=proyecto)
    if form.validate_on_submit():
        form.populate_obj(proyecto)
        db.session.commit()
        flash('Proyecto actualizado.', 'success')
        return redirect(url_for('projects.detalle', pid=pid))
    return render_template('projects/form.html',
                            form=form,
                            titulo_pagina=f'Editar: {proyecto.titulo}')

@projects.route('/<int:pid>/eliminar', methods=['POST'])
@login_required
def eliminar(pid):
    proyecto = Proyecto.query.get_or_404(pid)
    if proyecto.propietario_id != current_user.id and not current_user.es_admin:
        abort(403)
    db.session.delete(proyecto)
    db.session.commit()
    flash('Proyecto eliminado.', 'success')
    return redirect(url_for('projects.lista'))