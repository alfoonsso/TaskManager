from flask import Blueprint, render_template, abort, flash, redirect, url_for, request
from app.forms import ProyectoForm, BusquedaForm
# url_prefix='/proyectos' hace que TODAS las rutas de este Blueprint
# tengan /proyectos como prefijo automáticamente.
projects = Blueprint('projects', __name__, url_prefix='/proyectos')

PROYECTOS = [
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

CONTADOR = 4 # Simulamos el autoincremento de ID

@projects.route('/nuevo', methods=['GET', 'POST'])
def nuevo():
    form = ProyectoForm()
    # form.validate_on_submit() devuelve True únicamente cuando:
    # 1. La petición es POST (el usuario envió el formulario), Y
    # 2. Todos los validadores pasan (datos correctos).
    # En cualquier otro caso devuelve False:
    # - Petición GET (mostrar el formulario por primera vez)
    # - Petición POST con errores de validación
    if form.validate_on_submit():
        global CONTADOR
        nuevo_proyecto = {
        'id': CONTADOR,
        'titulo': form.titulo.data,
        'descripcion': form.descripcion.data or '',
        'fecha_limite':str(form.fecha_limite.data) if
        form.fecha_limite.data else None,
        'estado': 'activo',
        'tareas': []
        }
        PROYECTOS.append(nuevo_proyecto)
        CONTADOR += 1
        # flash() guarda el mensaje en la sesión para mostrarlo
        # en la SIGUIENTE petición (después del redirect).
        flash(f'Proyecto "{nuevo_proyecto["titulo"]}" creado correctamente.',
        'success')
        # Patrón PRG: después de un POST exitoso, siempre redirige.
        return redirect(url_for('projects.lista'))
    # GET o POST con errores: renderizar el formulario.
    # Si es POST con errores, form.titulo.errors contendrá los mensajes.
    return render_template('projects/form.html',
    form=form,
    titulo_pagina='Nuevo proyecto')

@projects.route('/<int:pid>/editar', methods=['GET', 'POST'])
def editar(pid):
    # Buscar el proyecto por ID
    proyecto = next((p for p in PROYECTOS if p['id'] == pid), None)
    if proyecto is None:
        from flask import abort
        abort(404)
    # Al instanciar el formulario con obj=proyecto,
    # WTForms rellena automáticamente los campos con los valores del objeto.
    # Esto funciona tanto con diccionarios como con objetos SQLAlchemy (U04).
    form = ProyectoForm(data=proyecto)

    if form.validate_on_submit():
        # Actualizar los datos del proyecto
        proyecto['titulo'] = form.titulo.data
        proyecto['descripcion'] = form.descripcion.data or ''
        proyecto['fecha_limite']= str(form.fecha_limite.data) 
        if form.fecha_limite.data:
            flash('Proyecto actualizado correctamente.', 'success')
            return redirect(url_for('projects.detalle', pid=pid))
        else:
            return None
        
    return render_template('projects/form.html',
                            form=form,
                            titulo_pagina=f'Editar: {proyecto["titulo"]}')

@projects.route('/', methods=['GET', 'POST'])
def lista():
    form_busqueda = BusquedaForm()
    proyectos = PROYECTOS.copy()
    q = ''

    # Leer el parámetro de búsqueda de la URL (/proyectos?q=texto)
    q = request.args.get('q', '').strip()
    if q:
        proyectos = [
            p for p in proyectos
            if q.lower() in p['titulo'].lower()
            or q.lower() in p.get('descripcion', '').lower()
        ]
    return render_template('projects/lista.html',
                            proyectos=proyectos,
                            form_busqueda=form_busqueda,
                            q=q,
                            total=len(PROYECTOS))

@projects.route('/<int:pid>')
def detalle(pid):
    proyecto = next((p for p in PROYECTOS if p['id'] == pid), None)
    if proyecto is None:
        abort(404)
    return render_template('projects/detalle.html', proyecto=proyecto)