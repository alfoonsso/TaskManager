import sys

print('=' * 50)
print('Verificación del entorno Flask')
print('=' * 50)
print(f'Python versión: {sys.version}')
print(f'Intérprete: {sys.executable}')
print()
paquetes = ['flask', 'flask_wtf', 'flask_sqlalchemy', 'flask_login']
for paquete in paquetes:
    try:
        modulo = __import__(paquete)
        version = getattr(modulo, '__version__', 'instalado')
        print(f' ✓ {paquete}: {version}')
    except ImportError:
        print(f' ✗ {paquete}: NO INSTALADO')
        print()
    if 'venv' in sys.executable:
        print('Entorno virtual: ACTIVO ✓')
    else:
        print('ATENCIÓN: El entorno virtual NO está activo.')
        print('Ejecuta: source venv/bin/activate')
