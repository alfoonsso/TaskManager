from flask import Blueprint, render_template, abort
# url_prefix='/proyectos' hace que TODAS las rutas de este Blueprint
# tengan /proyectos como prefijo automáticamente.
projects = Blueprint('projects', __name__, url_prefix='/proyectos')

PROYECTOS_PRUEBA = [
    {'id': 1, 'titulo': 'Rediseño web corporativa',
    'descripcion': 'Modernizar la web con nuevo diseño y mejor rendimiento.',
    'estado': 'activo', 'prioridad': 'alta',
    'tareas': [
    {'id': 1, 'titulo': 'Wireframes de la home', 'estado':
    'completada', 'prioridad': 'media'},
    {'id': 2, 'titulo': 'Implementar nuevo header', 'estado':
    'en_progreso','prioridad': 'alta'},
    {'id': 3, 'titulo': 'Optimizar imágenes', 'estado': 'pendiente',
    'prioridad': 'baja'},
    ]},
    {'id': 2, 'titulo': 'App móvil iOS/Android',
    'descripcion': 'Nueva aplicación móvil nativa para clientes.',
    'estado': 'activo', 'prioridad': 'urgente',
    'tareas': [
    {'id': 4, 'titulo': 'Configurar repositorio', 'estado':
    'completada', 'prioridad': 'alta'},
    {'id': 5, 'titulo': 'Diseño de la arquitectura', 'estado':
    'en_progreso', 'prioridad': 'urgente'},
    ]},
    {'id': 3, 'titulo': 'Migración de base de datos',
    'descripcion': 'Migrar de MySQL a PostgreSQL sin downtime.',
    'estado': 'pausado', 'prioridad': 'media', 'tareas': []},
    ]
@projects.route('/')
def lista():
     return render_template('projects/lista.html', proyectos=PROYECTOS_PRUEBA)

@projects.route('/<int:pid>')
def detalle(pid):
    proyecto = next((p for p in PROYECTOS_PRUEBA if p['id'] == pid), None)
    if proyecto is None:
        abort(404)

    return render_template('projects/detalle.html', proyecto=proyecto)
@projects.route('/nuevo')
def nuevo():
    return "Formulario para nuevo proyecto (Próximamente en U03)"

@projects.route('/<int:pid>/editar')
def editar(pid):
    proyecto = next((p for p in PROYECTOS_PRUEBA if p['id'] == pid), None)
    if proyecto is None:
        abort(404)
    return "Formulario para editar proyecto (Próximamente)"
