from flask import Blueprint, render_template, redirect, url_for, session, flash
auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
# Simulamos un login por ahora
    session['usuario'] = {'nombre': 'Usuario de Prueba'} # Login simulado
    flash('Has iniciado sesión correctamente', 'success')
    return redirect(url_for('main.index'))

@auth.route('/logout')
def logout():
    session.pop('usuario', None)
    flash('Has cerrado sesión', 'info')
    return redirect(url_for('main.index'))