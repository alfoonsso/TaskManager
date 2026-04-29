# api/main.py — versión completa
import logging
import traceback
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
from app.routers import projects, tasks

# ── Logging — ACT 7.3 punto 4 (opcional) ─────────────────────────────
# Registra errores 500 con la traza completa en un archivo.
# Los errores quedan en 'taskmanager.log' junto a main.py.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s  %(levelname)-8s  %(message)s',
    handlers=[
        logging.FileHandler('taskmanager.log', encoding='utf-8'),
        logging.StreamHandler(),   # también muestra en la consola de uvicorn
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

# ── Manejador para errores de validación Pydantic (422) ──────────────
# Se activa cuando el cliente envía datos con tipos incorrectos o
# campos obligatorios que faltan.
# Ejemplo: fecha_limite='hola' → 422 con detalle del campo fallido.
@app.exception_handler(RequestValidationError)
async def error_validacion(request: Request, exc: RequestValidationError):
    errores = []
    for error in exc.errors():
        # loc[0] es siempre 'body'/'query'/etc. — lo omitimos para mayor claridad
        campo = ' → '.join(str(parte) for parte in error['loc'][1:])
        errores.append({
            'campo': campo or 'body',
            'mensaje': error['msg'],
            'tipo': error['type'],
        })
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            'error': 'Error de validación',
            'detalle': errores,
        }
    )

# ── Manejador para errores de integridad de BD (409) ──────────────────
# Se activa cuando se viola una restricción de la BD
# (clave única duplicada, FK inexistente, etc.).
@app.exception_handler(IntegrityError)
async def error_integridad(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            'error': 'Conflicto de datos',
            'detalle': 'Un registro con esos datos ya existe',
        }
    )

# ── Manejador para errores internos del servidor (500) ─────────────────
# Última línea de defensa: captura cualquier excepción no manejada.
# Re-lanza HTTPException para que FastAPI la gestione con normalidad.
@app.exception_handler(Exception)
async def error_interno(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        raise exc  # dejar que FastAPI lo maneje normalmente

    # Registrar traza completa en el log (nunca mostrarla al cliente)
    logger.error(
        'Error interno en %s %s\n%s',
        request.method,
        request.url.path,
        traceback.format_exc(),
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={'error': 'Error interno del servidor'},
    )

# ── Routers ───────────────────────────────────────────────────────────
app.include_router(projects.router, prefix='/api/v1')
app.include_router(tasks.router, prefix='/api/v1')

# ── Endpoints de estado ───────────────────────────────────────────────
@app.get('/', tags=['Estado'])
def root():
    return {'mensaje': 'TaskManager API v1.0', 'documentacion': '/docs'}

@app.get('/health', tags=['Estado'])
def health():
    return {'status': 'ok'}