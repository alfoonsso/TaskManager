# web/app/models.py
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager
from datetime import datetime

# ── Tabla de unión para la relación muchos-a-muchos Tarea ↔ Etiqueta ──
# No es un modelo completo, sino una tabla auxiliar sin clase propia.
tarea_etiqueta = db.Table('tarea_etiqueta',
    db.Column('tarea_id', db.Integer, db.ForeignKey('tareas.id'),
    primary_key=True),
    db.Column('etiqueta_id', db.Integer, db.ForeignKey('etiquetas.id'),
    primary_key=True)
    )

# Flask-Login necesita esta función para cargar el usuario desde la sesión.
# Se ejecuta en CADA petición donde haya una sesión activa.
# Recibe el ID del usuario (como string) y devuelve el objeto Usuario.
@login_manager.user_loader
def cargar_usuario(user_id):
    return Usuario.query.get(int(user_id))

class Usuario(UserMixin, db.Model): # UserMixin PRIMERO, db.Model SEGUNDO
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    rol = db.Column(db.String(20), default='usuario') # 'usuario' o
    'admin'
    activo = db.Column(db.Boolean, default=True)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    proyectos = db.relationship('Proyecto', backref='propietario',
                                lazy='dynamic',
                                foreign_keys='Proyecto.propietario_id')
    
    # ── Métodos de seguridad ──────────────────────────────────────────
    def set_password(self, password):
        """Hashea la contraseña y la almacena. Nunca almacena texto plano."""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica si la contraseña introducida coincide con el hash."""
        return check_password_hash(self.password, password)
    
    # ── Propiedades de rol ────────────────────────────────────────────
    @property
    def es_admin(self):
        return self.rol == 'admin'
    
    # ── Sobrescribir is_active de UserMixin para respetar el campo 'activo' ──
    @property
    def is_active(self):
        """Un usuario desactivado no puede iniciar sesión aunque tenga cuenta."""
        return self.activo
    
    def __repr__(self):
        return f'<Usuario {self.email}>'
    
class Proyecto(db.Model):
    __tablename__ = 'proyectos'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    estado = db.Column(db.String(20), default='activo')
    fecha_limite = db.Column(db.Date)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    propietario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))

    # Relación: un proyecto tiene muchas tareas.
    # cascade='all, delete-orphan' → al borrar el proyecto se borran sus tareas.
    tareas = db.relationship('Tarea', backref='proyecto', lazy='dynamic',
    cascade='all, delete-orphan',
    order_by='Tarea.creado_en')

    @property
    def progreso(self):
        """Porcentaje de tareas completadas (0-100)."""
        total = self.tareas.count()
        if total == 0:
            return 0
        completadas = self.tareas.filter_by(estado='completada').count()
        return round(completadas / total * 100)
    
    @property
    def tareas_pendientes(self):
        return self.tareas.filter(Tarea.estado != 'completada').count()
    
    def __repr__(self):
        return f'<Proyecto {self.titulo}>'
    
class Tarea(db.Model):
    __tablename__ = 'tareas'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    prioridad = db.Column(db.String(20), default='media')
    estado = db.Column(db.String(20), default='pendiente')
    fecha_limite = db.Column(db.Date)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    proyecto_id = db.Column(db.Integer, db.ForeignKey('proyectos.id'))
    asignado_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'),
    nullable=True)

    # Relaciones
    comentarios = db.relationship('Comentario', backref='tarea',
    lazy='dynamic',
    cascade='all, delete-orphan')
    etiquetas = db.relationship('Etiqueta', secondary=tarea_etiqueta,
    backref=db.backref('tareas', lazy='dynamic'))

    def __repr__(self):
        return f'<Tarea {self.titulo}>'

class Comentario(db.Model):
    __tablename__ = 'comentarios'

    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    tarea_id = db.Column(db.Integer, db.ForeignKey('tareas.id'))
    autor_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    autor = db.relationship('Usuario', backref='comentarios')
    
    def __repr__(self):
        return f'<Comentario de {self.autor_id} en tarea {self.tarea_id}>'
    
class Etiqueta(db.Model):
    __tablename__ = 'etiquetas'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    color = db.Column(db.String(7), default='#3498db') # Color hexadecimal
    
    def __repr__(self):
        return f'<Etiqueta {self.nombre}>'