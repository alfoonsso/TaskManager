# api/app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app.database import get_db
from app.models import Usuario
from app.schemas import (
    UsuarioCreate, UsuarioResponse,
    TokenResponse, RefreshRequest, AccessTokenResponse,
)
from app.security import (
    hashear_password, verificar_password,
    crear_access_token, crear_refresh_token,
    get_current_user, SECRET_KEY, ALGORITHM,
)

router = APIRouter(prefix='/auth', tags=['Autenticación'])


# ── POST /auth/registro ───────────────────────────────────────────────
@router.post('/registro',
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary='Registrar un nuevo usuario')
def registro(datos: UsuarioCreate, db: Session = Depends(get_db)):
    # Verificar que el email no está registrado
    if db.query(Usuario).filter_by(email=datos.email.lower()).first():
        raise HTTPException(
            status_code=400,
            detail='Ya existe una cuenta con ese correo electrónico'
        )
    usuario = Usuario(
        nombre   = datos.nombre.strip(),
        email    = datos.email.lower().strip(),
        password = hashear_password(datos.password)
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


# ── POST /auth/token — Login ──────────────────────────────────────────
# OAuth2PasswordRequestForm espera datos de formulario (form data),
# NO JSON. En Swagger UI, muestra campos de texto para username y password.
@router.post('/token',
    response_model=TokenResponse,
    summary='Iniciar sesión y obtener tokens JWT')
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # OAuth2PasswordRequestForm usa 'username' (no 'email') por convención del estándar
    usuario = db.query(Usuario).filter_by(email=form.username.lower()).first()

    # Misma respuesta para email no encontrado y contraseña incorrecta.
    # No revelar cuál de los dos falló para dificultar ataques de enumeración.
    if not usuario or not verificar_password(form.password, usuario.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Correo electrónico o contraseña incorrectos',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Esta cuenta ha sido desactivada'
        )
    # Generar los tokens
    access_token  = crear_access_token({'sub': str(usuario.id), 'rol': usuario.rol})
    refresh_token = crear_refresh_token(usuario.id)
    return TokenResponse(
        access_token  = access_token,
        refresh_token = refresh_token
    )


# ── GET /auth/me — Perfil del usuario autenticado ─────────────────────
@router.get('/me',
    response_model=UsuarioResponse,
    summary='Obtener el perfil del usuario autenticado')
def mi_perfil(usuario: Usuario = Depends(get_current_user)):
    """Requiere autenticación. Devuelve los datos del usuario del token."""
    return usuario


# ── POST /auth/refresh — Renovar el access token ──────────────────────
@router.post('/refresh',
    response_model=AccessTokenResponse,
    summary='Renovar el access token con el refresh token')
def refresh(datos: RefreshRequest, db: Session = Depends(get_db)):
    excepcion = HTTPException(          # ← indentación correcta: dentro de la función
        status_code=401,
        detail='Refresh token inválido o expirado'
    )
    try:
        payload    = jwt.decode(datos.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id    = payload.get('sub')
        token_type = payload.get('type')
        # Verificar que es un refresh token, no un access token
        if token_type != 'refresh' or user_id is None:
            raise excepcion
    except JWTError:
        raise excepcion

    usuario = db.query(Usuario).filter_by(id=int(user_id), activo=True).first()
    if not usuario:
        raise excepcion

    # Generar nuevo access token con los datos actuales del usuario
    # (el rol puede haber cambiado desde que se generó el refresh token)
    nuevo_access = crear_access_token({'sub': str(usuario.id), 'rol': usuario.rol})
    return AccessTokenResponse(access_token=nuevo_access)