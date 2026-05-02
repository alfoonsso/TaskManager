# web/app/api_client.py
import requests
from flask import session, flash, redirect, url_for
from functools import wraps

API_BASE = 'http://127.0.0.1:8000/api/v1'
TIMEOUT = 10 # Segundos máximos de espera por respuesta


def _headers() -> dict:
    """
    Construye las cabeceras HTTP para la petición.
    Si hay un token JWT en la sesión Flask, lo incluye en Authorization.
    """
    headers = {'Content-Type': 'application/json'}
    token = session.get('access_token')
    if token:
        headers['Authorization'] = f'Bearer {token}'
    return headers

def _manejar_respuesta(resp: requests.Response) -> dict | list | None:
    """
    Procesa la respuesta de la API y devuelve los datos.
    Lanza excepciones específicas según el código de estado.
    """
    if resp.status_code == 204:
        return None # No Content: operación exitosa sin datos
    
    if resp.status_code == 401:
        # Token expirado o inválido → limpiar sesión y redirigir al login
        session.clear()
        raise APIError(401, 'Sesión expirada. Por favor, inicia sesión de nuevo.')
    
    if resp.status_code == 403:
        raise APIError(403, 'No tienes permiso para realizar esta acción.')
    
    if resp.status_code == 404:
        raise APIError(404, 'El recurso solicitado no existe.')
    
    if resp.status_code == 409:
        raise APIError(409, resp.json().get('detalle', 'Conflicto de datos.'))
    
    if resp.status_code >= 400:
        detalle = resp.json().get('detail', 'Error en la petición.')
        raise APIError(resp.status_code, detalle)
    
    return resp.json()


class APIError(Exception):
    """Excepción personalizada para errores de la API."""
    def __init__(self, status_code: int, mensaje: str):
        self.status_code = status_code
        self.mensaje = mensaje
        super().__init__(mensaje)

class APIClient:
    """Cliente HTTP para comunicarse con la API FastAPI de TaskManager."""
    
    @staticmethod
    def get(endpoint: str, params: dict = None) -> dict | list:
        """Petición GET al endpoint dado."""
        try:
            resp = requests.get(
                f'{API_BASE}{endpoint}',
                headers = _headers(),
                params = params,
                timeout = TIMEOUT
            )
            return _manejar_respuesta(resp)
        except requests.ConnectionError:
            raise APIError(503, 'La API no está disponible. Verifica que está arrancada.')
        except requests.Timeout:
            raise APIError(504, 'La API tardó demasiado en responder.')
        
    @staticmethod
    def post(endpoint: str, datos: dict) -> dict:
        """Petición POST con datos JSON."""
        try:
            resp = requests.post(
                f'{API_BASE}{endpoint}',
                json = datos,
                headers = _headers(),
                timeout = TIMEOUT
            )
            return _manejar_respuesta(resp)
        except requests.ConnectionError:
            raise APIError(503, 'La API no está disponible.')
        except requests.Timeout:
            raise APIError(504, 'Timeout al contactar con la API.')

    @staticmethod
    def patch(endpoint: str, datos: dict) -> dict:
        """Petición PATCH con datos parciales JSON."""
        try:
            resp = requests.patch(
                f'{API_BASE}{endpoint}',
                json = datos,
                headers = _headers(),
                timeout = TIMEOUT
            )
            return _manejar_respuesta(resp)
        except requests.ConnectionError:
            raise APIError(503, 'La API no está disponible.')
        
    @staticmethod
    def delete(endpoint: str) -> None:
        """Petición DELETE. No devuelve datos (204 No Content)."""
        try:
            resp = requests.delete(
                f'{API_BASE}{endpoint}',
                headers = _headers(),
                timeout = TIMEOUT
            )
            _manejar_respuesta(resp)
        except requests.ConnectionError:
            raise APIError(503, 'La API no está disponible.')
        
    @staticmethod
    def post_form(endpoint: str, datos: dict) -> dict:
        """Petición POST con datos de formulario (form data, no JSON).
        Necesario para el endpoint de login (/auth/token) que usa OAuth2.
        """
        try:
            resp = requests.post(
                f'{API_BASE}{endpoint}',
                data = datos, # 'data' para form, 'json' para JSON
                timeout = TIMEOUT
            )
            return _manejar_respuesta(resp)
        except requests.ConnectionError:
            raise APIError(503, 'La API no está disponible.')