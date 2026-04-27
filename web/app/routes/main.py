from flask import Blueprint, render_template, redirect, url_for, flash
from app.decoradores import solo_admin
from app.models import Usuario, Proyecto, Tarea
from flask_login import login_required, current_user
from app.forms import FormularioVacio
from app import db

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

@main.route('/admin')
@login_required
@solo_admin
def admin():
    proyectos = Proyecto.query.order_by(Proyecto.creado_en.desc()).all()
    usuarios = Usuario.query.order_by(Usuario.creado_en.desc()).all()

    total_proyectos = Proyecto.query.count()
    total_tareas = Tarea.query.count()
    usuarios_activos = Usuario.query.filter_by(activo=True).count()

    return render_template('admin/panel.html',
                        proyectos=proyectos,
                        usuarios=usuarios,
                        total_proyectos=total_proyectos,
                        total_tareas=total_tareas,
                        usuarios_activos=usuarios_activos,
                        form=FormularioVacio())

@main.route('/admin/usuarios/<int:uid>/toggle-activo', methods=['POST'])
@login_required
@solo_admin
def toggle_activo(uid):
    usuario = Usuario.query.get_or_404(uid)
    if usuario == current_user:
        flash('No puedes desactivar tu propia cuenta.', 'danger')
    else:
        usuario.activo = not usuario.activo
        db.session.commit()
        estado = 'activado' if usuario.activo else 'desactivado'
        flash(f'Usuario {usuario.nombre} {estado}.', 'success')
    return redirect(url_for('main.admin'))
