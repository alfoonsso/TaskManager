# web/app/routes/auth.py — actualizar login para obtener JWT de la API
from flask import Blueprint, render_template, flash, redirect, url_for, session
from flask_login import login_user, logout_user, login_required, current_user
from app.forms import LoginForm, RegistroForm
from app.api_client import APIClient, APIError
from app import db
from app.models import Usuario

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistroForm()
    if form.validate_on_submit():
        try:
            # 1. Crear la cuenta en la API
            APIClient.post('/auth/registro', {
                'nombre': form.nombre.data.strip(),
                'email': form.email.data.lower(),
                'password': form.password.data
            })
            flash('¡Cuenta creada! Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('auth.login'))
        except APIError as e:
            flash(e.mensaje, 'error')

    return render_template('auth/registro.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        try:
            # 1. Obtener los tokens JWT de la API (necesita form data, no JSON)
            tokens = APIClient.post_form('/auth/token', {
                'username': form.email.data.lower(),
                'password': form.password.data
            })

            # 2. Guardar los tokens en la sesión Flask
            session['access_token'] = tokens['access_token']
            session['refresh_token'] = tokens['refresh_token']

            # 3. Cargar el usuario desde la BD local para Flask-Login
            # (Flask-Login necesita un objeto Usuario de SQLAlchemy)
            usuario = Usuario.query.filter_by(email=form.email.data.lower()).first()
            if usuario:
                login_user(usuario, remember=form.recordarme.data)

            flash(f'¡Bienvenido, {tokens.get("nombre", "")}!', 'success')
            return redirect(url_for('main.index'))
        
        except APIError as e:
            flash(e.mensaje, 'error')

    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('access_token', None) # Limpiar el JWT también
    session.pop('refresh_token', None)
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('main.index'))