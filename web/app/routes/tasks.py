from flask import Blueprint, render_template
from .projects import PROYECTOS

tasks = Blueprint('tasks', __name__)

ORDEN = {'urgente': 0, 'alta': 1, 'media': 2, 'baja': 3}

@tasks.route('/tareas')
def mis_tareas():
    todas = []
    for proyecto in PROYECTOS:
        for tarea in proyecto['tareas']:
            tarea['proyecto'] = proyecto['titulo']
            todas.append(tarea)
    todas.sort(key=lambda t: ORDEN.get(t['prioridad'], 99))
    return render_template('tasks/lista.html', tareas=todas)

@tasks.route('/<int:pid>/tareas/nueva')
def nueva(pid):
    return "Nueva tarea (Próximamente)"

@tasks.route('/<int:pid>/tareas/<int:tid>/editar')
def editar(pid, tid):
    return "Editar tarea (Próximamente)"

@tasks.route('/<int:pid>/tareas/<int:tid>/eliminar', methods=['POST'])
def eliminar(pid, tid):
    return "Eliminar tarea (Próximamente)"