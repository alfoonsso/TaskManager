from flask import Blueprint, render_template
tasks = Blueprint('tasks', __name__)

@tasks.route('/mis-tareas')
def mis_tareas():
    return render_template('projects/lista.html', proyectos=[], tareas=[])