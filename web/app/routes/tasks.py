from flask import Blueprint, render_template, redirect, url_for, flash, abort
from app import db
from app.models import Proyecto, Tarea
from app.forms import TareaForm

tasks = Blueprint('tasks', __name__, url_prefix='/proyectos')

ORDEN_PRIORIDAD = {'urgente': 0, 'alta': 1, 'media': 2, 'baja': 3}

@tasks.route('/<int:pid>/tareas/nueva', methods=['GET', 'POST'])
def nueva(pid):
    proyecto = Proyecto.query.get_or_404(pid)
    form = TareaForm()
    if form.validate_on_submit():
        tarea = Tarea(
            titulo=form.titulo.data,
            descripcion=form.descripcion.data,
            prioridad=form.prioridad.data,
            estado=form.estado.data,
            fecha_limite=form.fecha_limite.data,
            proyecto_id=pid
        )
        db.session.add(tarea)
        db.session.commit()
        flash(f'Tarea "{tarea.titulo}" creada.', 'success')
        return redirect(url_for('projects.detalle', pid=pid))
    return render_template('tasks/form.html', form=form,
                            proyecto=proyecto,
                            titulo_pagina='Nueva tarea')

@tasks.route('/<int:pid>/tareas/<int:tid>/editar', methods=['GET', 'POST'])
def editar(pid, tid):
    proyecto = Proyecto.query.get_or_404(pid)
    tarea = Tarea.query.get_or_404(tid)
    form = TareaForm(obj=tarea)
    if form.validate_on_submit():
        form.populate_obj(tarea)
        db.session.commit()
        flash('Tarea actualizada.', 'success')
        return redirect(url_for('projects.detalle', pid=pid))
    return render_template('tasks/form.html', form=form,
                            proyecto=proyecto,
                            titulo_pagina=f'Editar: {tarea.titulo}')

@tasks.route('/<int:pid>/tareas/<int:tid>/eliminar', methods=['POST'])
def eliminar(pid, tid):
    tarea = Tarea.query.get_or_404(tid)
    db.session.delete(tarea)
    db.session.commit()
    flash('Tarea eliminada.', 'success')
    return redirect(url_for('projects.detalle', pid=pid))

@tasks.route('/tareas')
def mis_tareas():
    tareas = Tarea.query.all()
    tareas.sort(key=lambda t: ORDEN_PRIORIDAD.get(t.prioridad, 99))
    return render_template('tasks/lista.html', tareas=tareas)