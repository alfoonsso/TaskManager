# web/app/routes/tasks.py
from flask import Blueprint, render_template, flash, redirect, url_for, request, abort
from app.forms import TareaForm

tasks = Blueprint('tasks', __name__)
# Referencia a la lista de proyectos (en U04 vendrá de la BD)
# Por ahora importamos la lista de projects.py
from app.routes.projects import PROYECTOS
@tasks.route('/proyectos/<int:pid>/tareas/nueva', methods=['GET', 'POST'])
def nueva(pid):
    proyecto = next((p for p in PROYECTOS if p['id'] == pid), None)
    if not proyecto:
        abort(404)
    form = TareaForm()
    if form.validate_on_submit():
        # Calcular el próximo ID de tarea
        todas_tareas = [t for p in PROYECTOS for t in p['tareas']]
        nuevo_id = max((t['id'] for t in todas_tareas), default=0) + 1
        nueva_tarea = {
            'id': nuevo_id,
            'titulo': form.titulo.data,
            'descripcion': form.descripcion.data or '',
            'prioridad': form.prioridad.data,
            'estado': form.estado.data,
            'fecha_limite':str(form.fecha_limite.data) if
            form.fecha_limite.data else None,
        }
        proyecto['tareas'].append(nueva_tarea)
        flash(f'Tarea "{nueva_tarea["titulo"]}" creada.', 'success')
        return redirect(url_for('projects.detalle', pid=pid))
                    
    return render_template('tasks/form.html',
                            form=form,
                            proyecto=proyecto,
                            titulo_pagina=f'Nueva tarea en {proyecto["titulo"]}')

@tasks.route('/proyectos/<int:pid>/tareas/<int:tid>/editar', methods=['GET',
'POST'])
def editar(pid, tid):
    proyecto = next((p for p in PROYECTOS if p['id'] == pid), None)
    tarea = next((t for t in proyecto['tareas'] if t['id'] == tid), None) if proyecto else None
    if not proyecto or not tarea:
        abort(404)

    form = TareaForm(data=tarea)
    if form.validate_on_submit():
        tarea['titulo'] = form.titulo.data
        tarea['descripcion'] = form.descripcion.data or ''
        tarea['prioridad'] = form.prioridad.data
        tarea['estado'] = form.estado.data
        tarea['fecha_limite']= str(form.fecha_limite.data) if form.fecha_limite.data else None
        flash('Tarea actualizada.', 'success')
        return redirect(url_for('projects.detalle', pid=pid))
    
    return render_template('tasks/form.html',
                            form=form,
                            proyecto=proyecto,
                            titulo_pagina=f'Editar tarea')

@tasks.route('/proyectos/<int:pid>/tareas/<int:tid>/eliminar',
methods=['POST'])
def eliminar(pid, tid):
    proyecto = next((p for p in PROYECTOS if p['id'] == pid), None)
    if not proyecto:
        abort(404)

    proyecto['tareas'] = [t for t in proyecto['tareas'] if t['id'] != tid]
    flash('Tarea eliminada.', 'success')
    return redirect(url_for('projects.detalle', pid=pid))

@tasks.route('/mis-tareas')
def mis_tareas():
    # Recopilar todas las tareas de todos los proyectos
    todas = []
    for p in PROYECTOS:
        for t in p['tareas']:
            todas.append({**t, 'proyecto': p['titulo'], 'proyecto_id': p['id']})

    # Ordenar por prioridad
    orden = {'urgente': 0, 'alta': 1, 'media': 2, 'baja': 3}
    todas.sort(key=lambda t: orden.get(t['prioridad'], 99))

    return render_template('tasks/lista.html', tareas=todas)