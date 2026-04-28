# api/main.py — aplicación mínima inicial
from fastapi import FastAPI

# Crear la instancia de la aplicación con metadatos para la documentación
app = FastAPI(
    title = 'TaskManager API',
    description = 'API REST para la gestión de proyectos y tareas',
    version = '1.0.0'
    )

# Endpoint raíz — equivalente a @app.route('/') en Flask
@app.get('/')
def root():
    # FastAPI convierte el diccionario a JSON automáticamente
    # En Flask necesitaríamos jsonify(). Aquí no hace falta.
    return {'mensaje': 'TaskManager API v1.0', 'estado': 'activa'}

@app.get('/health')
def health_check():
    """Endpoint para verificar que el servicio está funcionando."""
    return {'status': 'ok'}
