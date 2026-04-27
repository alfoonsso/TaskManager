from functools import wraps
from flask import abort
from flask_login import current_user

def solo_admin(f):
    """Decorador que permite el acceso solo a usuarios con rol 'admin'."""
    @wraps(f) # Preserva el nombre y docstring de la función original
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401) # No autenticado
        if not current_user.es_admin:
            abort(403) # Autenticado pero sin permiso
        return f(*args, **kwargs)
    
    return decorated

def propietario_o_admin(obtener_proyecto):
    """
    Decorador de fábrica: verifica que el usuario autenticado es
    el propietario del recurso O tiene rol admin.
    'obtener_proyecto' es una función que recibe los kwargs de la ruta
    y devuelve el objeto a proteger.
    """
    def decorador(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            recurso = obtener_proyecto(kwargs)
            if recurso.propietario_id != current_user.id and not current_user.es_admin:
                abort(403)
            return f(*args, **kwargs)
        return decorated
    return decorador
