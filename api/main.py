# api/main.py — versión completa con autenticación JWT
import logging
import traceback
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
from app.routers import projects, tasks, auth   # ← 'users' eliminado: no existe aún

# ── Logging ───────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s  %(levelname)-8s  %(message)s',
    handlers=[
        logging.FileHandler('taskmanager.log', encoding='utf-8'),
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger('taskmanager')

# ── Aplicación ────────────────────────────────────────────────────────
app = FastAPI(
    title='TaskManager API',
    description='''
    ## API REST para TaskManager
    Gestiona proyectos, tareas y usuarios.
    La documentación completa está disponible en /docs.
    ''',
    version='1.0.0'
)

# ── CORS ──────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost:5000',
        'http://127.0.0.1:5000',
    ],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# ── Manejadores de error globales ─────────────────────────────────────
@app.exception_handler(RequestValidationError)
async def error_validacion(request: Request, exc: RequestValidationError):
    errores = []
    for error in exc.errors():
        campo = ' → '.join(str(parte) for parte in error['loc'][1:])
        errores.append({
            'campo':   campo or 'body',
            'mensaje': error['msg'],
            'tipo':    error['type'],
        })
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={'error': 'Error de validación', 'detalle': errores}
    )

@app.exception_handler(IntegrityError)
async def error_integridad(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            'error':   'Conflicto de datos',
            'detalle': 'Un registro con esos datos ya existe',
        }
    )

@app.exception_handler(Exception)
async def error_interno(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        raise exc   # dejar que FastAPI lo maneje normalmente
    logger.error('Error interno en %s %s\n%s',
                 request.method, request.url.path, traceback.format_exc())
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={'error': 'Error interno del servidor'}
    )

# ── Routers — registrados UNA sola vez con el prefijo ────────────────
# auth primero para que /docs muestre el botón Authorize correctamente
PREFIX = '/api/v1'
app.include_router(auth.router,     prefix=PREFIX)
app.include_router(projects.router, prefix=PREFIX)
app.include_router(tasks.router,    prefix=PREFIX)

# ── Endpoints de estado ───────────────────────────────────────────────
@app.get('/', tags=['Estado'])
def root():
    return {'mensaje': 'TaskManager API v1.0', 'documentacion': '/docs'}

@app.get('/health', tags=['Estado'])
def health():
    return {'status': 'ok'}