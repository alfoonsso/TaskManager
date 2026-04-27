from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import Usuario
from app.forms import RegistroForm, LoginForm


auth = Blueprint('auth', __name__, url_prefix='/auth')

# ── Registro ─────────────────────────────────────────────────────────
@auth.route('/registro', methods=['GET', 'POST'])
def registro():
    # Si ya está autenticado, redirigir al dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistroForm()
    if form.validate_on_submit():
        # Verificar que el email no está ya registrado
        if Usuario.query.filter_by(email=form.email.data.lower()).first():
            flash('Ya existe una cuenta con ese correo electrónico. ¿Quieres iniciar sesión?', 'error')
            return redirect(url_for('auth.registro'))
    
        # Crear el usuario (sin guardar la contraseña en texto plano)
        usuario = Usuario(
                    nombre = form.nombre.data.strip(),
                    email = form.email.data.lower().strip()
                    )
        usuario.set_password(form.password.data) # Hashea la contraseña
        db.session.add(usuario)
        db.session.commit()

        flash('¡Cuenta creada con éxito! Ya puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/registro.html', form=form)

# ── Login ─────────────────────────────────────────────────────────────
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data.lower()).first()
    
        # Verificar usuario, contraseña Y que la cuenta esté activa
        if usuario and usuario.check_password(form.password.data) and usuario.is_active:
            # login_user() abre la sesión: guarda el ID del usuario en la cookie
            # remember=True crea una cookie persistente (no se borra al cerrar el navegador)
            login_user(usuario, remember=form.recordarme.data)
            # Si el usuario intentaba acceder a una página protegida antes del login,
            # Flask-Login guarda esa URL en el parámetro 'next'.
            # Redirigimos ahí después del login para no perder lo que buscaba.
            next_page = request.args.get('next')
            # Seguridad: verificar que 'next' es una URL relativa (no externa)
            # para evitar ataques de redirección abierta.
            if next_page and not next_page.startswith('http'):
                return redirect(next_page)
            
            flash(f'¡Bienvenido de nuevo, {usuario.nombre}!', 'success')
            return redirect(url_for('main.index'))
        
        # Mensaje de error intencionalmente vago: no revelar si el email existe
        flash('Correo electrónico o contraseña incorrectos.', 'error')
    
    return render_template('auth/login.html', form=form)

# ── Logout ────────────────────────────────────────────────────────────
@auth.route('/logout')
@login_required # Solo puede hacer logout quien esté autenticado
def logout():
    nombre = current_user.nombre
    logout_user() # Elimina la sesión del usuario
    flash(f'Hasta pronto, {nombre}. Sesión cerrada correctamente.', 'info')
    return redirect(url_for('main.index'))
