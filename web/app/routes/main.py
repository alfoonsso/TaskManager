from flask import Blueprint, render_template
main = Blueprint('main', __name__)
@main.route('/')
def index():
    tareas_urgentes = [
    {'titulo': 'Revisar pull request #47', 'proyecto': 'Rediseño web',
    'prioridad': 'urgente'},
    {'titulo': 'Preparar despliegue v2.1', 'proyecto': 'App móvil',
    'prioridad': 'alta'},
    {'titulo': 'Corregir bug en el login', 'proyecto': 'Backend API',
    'prioridad': 'urgente'},
    ]
    
    proyectos_activos = [
    {'titulo': 'Rediseño web', 'tareas_total': 8, 'completadas': 3},
     {'titulo': 'App móvil', 'tareas_total': 12, 'completadas': 9},
    {'titulo': 'Backend API', 'tareas_total': 5, 'completadas': 1},
    ]
    total_pendientes = sum(p['tareas_total'] - p['completadas'] for p in
    proyectos_activos)

    return render_template('index.html',
    tareas_urgentes = tareas_urgentes,
    proyectos_activos = proyectos_activos,
    total_proyectos = len(proyectos_activos),
    total_pendientes = total_pendientes,
    )
