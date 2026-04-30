# api/app/security.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Usuario
import os


# ── Configuración ────────────────────────────────────────────────────
# La SECRET_KEY DEBE estar en una variable de entorno en producción.
# Genera una segura con: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'CAMBIAR-EN-PRODUCCION-usar-secrets.token_hex-32'
ALGORITHM = 'HS256'     # Algoritmo de firma (HMAC-SHA256)
ACCESS_EXPIRE  = 60     # Minutos que dura el access token
REFRESH_EXPIRE = 7      # Días que dura el refresh token


# ── Hashing de contraseñas ────────────────────────────────────────────
# CryptContext gestiona el esquema de hashing.
# bcrypt es el algoritmo recomendado para contraseñas.
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def hashear_password(password: str) -> str:
    """Hashea una contraseña en texto plano usando bcrypt."""
    return pwd_context.hash(password)

def verificar_password(password_plano: str, password_hash: str) -> bool:
    """Verifica si una contraseña coincide con su hash."""
    return pwd_context.verify(password_plano, password_hash)


# ── Generación de tokens ─────────────────────────────────────────────
def crear_access_token(data: dict,
                       expires_delta: Optional[timedelta] = None) -> str:
    """
    Genera un access token JWT.
    data: diccionario con los datos a incluir en el payload.
    expires_delta: tiempo de vida personalizado (por defecto ACCESS_EXPIRE minutos).
    """
    payload = data.copy()
    expira  = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_EXPIRE))
    payload.update({'exp': expira, 'type': 'access'})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def crear_refresh_token(user_id: int) -> str:
    """
    Genera un refresh token JWT.
    Contiene mínima información: solo el ID del usuario.
    """
    payload = {
        'sub':  str(user_id),
        'type': 'refresh',
        'exp':  datetime.utcnow() + timedelta(days=REFRESH_EXPIRE)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# ── OAuth2 ────────────────────────────────────────────────────────────
# OAuth2PasswordBearer extrae automáticamente el token de la cabecera:
#   Authorization: Bearer <token>
# tokenUrl es la URL del endpoint de login (aparece en Swagger UI).
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/token')


# ── Dependencias de autenticación ────────────────────────────────────
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Usuario:
    """
    Dependencia que extrae y verifica el token JWT de la cabecera.
    Devuelve el objeto Usuario autenticado o lanza 401 si el token es inválido.
    """
    excepcion_credenciales = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail      = 'Token inválido o expirado',
        headers     = {'WWW-Authenticate': 'Bearer'},   # Estándar HTTP
    )
    try:
        payload    = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id    = payload.get('sub')
        token_type = payload.get('type')
        # Verificar que el payload tiene los campos esperados
        if user_id is None or token_type != 'access':
            raise excepcion_credenciales
    except JWTError:
        # Captura: token malformado, firma incorrecta, token expirado
        raise excepcion_credenciales

    # Cargar el usuario desde la BD
    usuario = db.query(Usuario).filter_by(id=int(user_id)).first()
    if not usuario or not usuario.activo:
        raise excepcion_credenciales
    return usuario


def get_current_user_opcional(
    token: Optional[str] = Depends(oauth2_scheme),  # ← indentación correcta
    db: Session = Depends(get_db)
) -> Optional[Usuario]:
    """
    Dependencia para endpoints que funcionan con o sin autenticación.
    Si hay token válido devuelve el usuario; si no, devuelve None.
    """
    if not token:
        return None
    try:
        return get_current_user(token, db)
    except HTTPException:
        return None


def require_admin(
    usuario: Usuario = Depends(get_current_user)    # ← indentación correcta
) -> Usuario:
    """
    Dependencia que exige rol de administrador.
    Si el usuario está autenticado pero no es admin, lanza 403.
    """
    if not usuario.es_admin:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail      = 'Esta operación requiere permisos de administrador'
        )
    return usuario