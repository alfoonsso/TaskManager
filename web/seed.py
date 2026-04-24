# web/seed.py
from app import create_app, db
from app.models import Usuario, Proyecto, Tarea, Etiqueta
from datetime import date, timedelta

app = create_app()

with app.app_context():
    # Eliminar todos los datos existentes y recrear las tablas
    # CUIDADO: esto borra todo. Solo usar en desarrollo.
    db.drop_all()
    db.create_all()

    # ── Usuarios ────────────────────────────────────────────────────────
    admin = Usuario(nombre='Admin TaskManager', email='admin@taskmanager.com',
    rol='admin')
    admin.set_password('admin1234')

    ana = Usuario(nombre='Ana García', email='ana@taskmanager.com')
    ana.set_password('password123')

    pablo = Usuario(nombre='Pablo López', email='pablo@taskmanager.com')
    pablo.set_password('password123')

    db.session.add_all([admin, ana, pablo])
    db.session.flush() # Obtener los IDs sin hacer commit todavía

    # ── Etiquetas ────────────────────────────────────────────────────────
    e_frontend = Etiqueta(nombre='frontend', color='#3498db')
    e_backend = Etiqueta(nombre='backend', color='#e74c3c')
    e_bug = Etiqueta(nombre='bug', color='#e67e22')
    e_mejora = Etiqueta(nombre='mejora', color='#2ecc71')
    e_docs = Etiqueta(nombre='documentación',color='#9b59b6')
    db.session.add_all([e_frontend, e_backend, e_bug, e_mejora, e_docs])
    db.session.flush()

    # ── Proyectos ────────────────────────────────────────────────────────
    p1 = Proyecto(
        titulo = 'Rediseño web corporativa',
        descripcion = 'Modernizar la web con nuevo diseño y mejor rendimiento.',
        estado = 'activo',
        fecha_limite = date.today() + timedelta(days=45),
        propietario_id = ana.id
        )
    p2 = Proyecto(
        titulo = 'App móvil iOS/Android',
        descripcion = 'Nueva aplicación móvil nativa para los clientes.',
        estado = 'activo',
        fecha_limite = date.today() + timedelta(days=90),
        propietario_id = pablo.id
        )
    p3 = Proyecto(
        titulo = 'Migración de base de datos',
        descripcion = 'Migrar de MySQL a PostgreSQL sin downtime.',
        estado = 'pausado',
        propietario_id = admin.id
        )
    db.session.add_all([p1, p2, p3])
    db.session.flush()

    # ── Tareas ───────────────────────────────────────────────────────────
    tareas_p1 = [
        Tarea(titulo='Diseñar wireframes de la home',
        prioridad='alta', estado='completada', proyecto_id=p1.id,
        asignado_id=ana.id),
        Tarea(titulo='Implementar nuevo header responsive',
        prioridad='alta', estado='en_progreso', proyecto_id=p1.id,
        asignado_id=pablo.id,
        fecha_limite=date.today() + timedelta(days=7)),
        Tarea(titulo='Optimizar imágenes para web',
        prioridad='media', estado='pendiente', proyecto_id=p1.id),
        Tarea(titulo='Implementar modo oscuro',
        prioridad='baja', estado='pendiente', proyecto_id=p1.id),
        Tarea(titulo='Corregir bug en el formulario de contacto',
        prioridad='urgente', estado='pendiente', proyecto_id=p1.id,
        asignado_id=pablo.id),
        ]
    tareas_p2 = [
        Tarea(titulo='Configurar repositorio y CI/CD',
        prioridad='alta', estado='completada', proyecto_id=p2.id),
        Tarea(titulo='Diseñar arquitectura de la app',
        prioridad='urgente', estado='en_progreso', proyecto_id=p2.id,
        asignado_id=ana.id),
        Tarea(titulo='Implementar autenticación con JWT',
        prioridad='alta', estado='pendiente', proyecto_id=p2.id),
        ]
    db.session.add_all(tareas_p1 + tareas_p2)
    db.session.flush()

    # Añadir etiquetas a algunas tareas
    tareas_p1[0].etiquetas.append(e_frontend)
    tareas_p1[1].etiquetas.extend([e_frontend, e_mejora])
    tareas_p1[4].etiquetas.extend([e_bug, e_frontend])
    tareas_p2[2].etiquetas.extend([e_backend, e_mejora])

    db.session.commit()
    print('✓ Base de datos poblada correctamente.')
    print(f' Usuarios: {Usuario.query.count()}')
    print(f' Proyectos: {Proyecto.query.count()}')
    print(f' Tareas: {Tarea.query.count()}')
    print(f' Etiquetas: {Etiqueta.query.count()}')
