from flask import Blueprint, render_template
tasks = Blueprint('tasks', __name__)

@tasks.route('/mis-tareas')
def mis_tareas():
    return render_template('projects/lista.html', proyectos=[], tareas=[])

@tasks.route('/<int:pid>/tareas/nueva')
def nueva(pid):
    return "Nueva tarea (Próximamente)"

@tasks.route('/<int:pid>/tareas/<int:tid>/editar')
def editar(pid, tid):
    return "Editar tarea (Próximamente)"

@tasks.route('/<int:pid>/tareas/<int:tid>/eliminar', methods=['POST'])
def eliminar(pid, tid):
    return "Eliminar tarea (Próximamente)"