from flask import Blueprint, render_template, abort, flash, redirect, url_for, request
from app.forms import ProyectoForm, BusquedaForm, FormularioVacio
from app import db
from app.models import Proyecto, Tarea
# url_prefix='/proyectos' hace que TODAS las rutas de este Blueprint
# tengan /proyectos como prefijo automáticamente.
projects = Blueprint('projects', __name__, url_prefix='/proyectos')

@projects.route('/')
def lista():
    # Leer el parámetro de búsqueda de la URL (/proyectos?q=texto)
    q = request.args.get('q', '').strip()
    pagina = request.args.get('pagina', 1, type=int)
    query = Proyecto.query.order_by(Proyecto.creado_en.desc())

    if q:
        query = query.filter(
            db.or_(Proyecto.titulo.ilike(f'%{q}%'),
            Proyecto.descripcion.ilike(f'%{q}%'))
            )
        
    paginacion = query.paginate(page=pagina, per_page=10, error_out=False)    
    return render_template('projects/lista.html',
                            proyectos = paginacion.items,                                
                            paginacion = paginacion,
                            q = q,
                            form_busqueda = BusquedaForm())

@projects.route('/<int:pid>')
def detalle(pid):
    proyecto = Proyecto.query.get_or_404(pid)
    tareas = proyecto.tareas.order_by(Tarea.creado_en.desc()).all()
    return render_template('projects/detalle.html',
                            proyecto=proyecto,
                            tareas=tareas,
                            form=FormularioVacio())

@projects.route('/nuevo', methods=['GET', 'POST'])
def nuevo():
    form = ProyectoForm()
    if form.validate_on_submit():
        proyecto = Proyecto(
                    titulo = form.titulo.data,
                    descripcion = form.descripcion.data,
                    fecha_limite = form.fecha_limite.data,
                    propietario_id = 1 # En U05 usaremos current_user.id
                    )
        db.session.add(proyecto)
        db.session.commit()
        flash(f'Proyecto "{proyecto.titulo}" creado.', 'success')
        return redirect(url_for('projects.lista'))
    
    return render_template('projects/form.html',
                            form=form, titulo_pagina='Nuevo proyecto')

@projects.route('/<int:pid>/editar', methods=['GET', 'POST'])
def editar(pid):
    proyecto = Proyecto.query.get_or_404(pid)
    form = ProyectoForm(obj=proyecto)
    if form.validate_on_submit():
        form.populate_obj(proyecto) # Rellena el objeto con los datos del form
        db.session.commit()
        flash('Proyecto actualizado.', 'success')
        return redirect(url_for('projects.detalle', pid=pid))
    
    return render_template('projects/form.html',
                            form=form,
                            titulo_pagina=f'Editar: {proyecto.titulo}')

@projects.route('/<int:pid>/eliminar', methods=['POST'])
def eliminar(pid):
    proyecto = Proyecto.query.get_or_404(pid)
    db.session.delete(proyecto) # cascade elimina sus tareas y comentarios
    db.session.commit()
    flash('Proyecto eliminado.', 'success')
    return redirect(url_for('projects.lista'))