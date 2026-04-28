# api/main.py — versión completa
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import projects, tasks

app = FastAPI(
        title = 'TaskManager API',
        description = '''
        ## API REST para TaskManager
        Gestiona proyectos, tareas y usuarios.
        La documentación completa está disponible en /docs.
        ''',
        version = '1.0.0'
        )

# CORS: permitir peticiones desde el frontend Flask (puerto 5000)
# Sin esto, el navegador bloqueará las peticiones de Flask a FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins = [
    'http://localhost:5000',
    'http://127.0.0.1:5000',
    ],
    allow_credentials= True,
    allow_methods = ['*'],
    allow_headers = ['*'],
)

# Registrar routers con prefijo de versión en la URL
app.include_router(projects.router, prefix='/api/v1')
app.include_router(tasks.router, prefix='/api/v1')

@app.get('/', tags=['Estado'])
def root():
    return {'mensaje': 'TaskManager API v1.0', 'documentacion': '/docs'}

@app.get('/health', tags=['Estado'])
def health():
    return {'status': 'ok'}