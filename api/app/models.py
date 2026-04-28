# api/app/models.py
# Versión simplificada: solo SQLAlchemy, sin dependencias de Flask
from sqlalchemy import Column, Integer, String, Boolean, Text, Date
from sqlalchemy import DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

# Tabla de unión muchos-a-muchos
tarea_etiqueta = Table('tarea_etiqueta', Base.metadata,
    Column('tarea_id', Integer, ForeignKey('tareas.id'),
        primary_key=True),
    Column('etiqueta_id', Integer, ForeignKey('etiquetas.id'),
        primary_key=True)
    )

class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password = Column(String(256), nullable=False)
    rol = Column(String(20), default='usuario')
    activo = Column(Boolean, default=True)
    creado_en = Column(DateTime, default=datetime.utcnow)
    proyectos = relationship('Proyecto', back_populates='propietario')

class Proyecto(Base):
    __tablename__ = 'proyectos'
    id = Column(Integer, primary_key=True)
    titulo = Column(String(100), nullable=False)
    descripcion = Column(Text)
    estado = Column(String(20), default='activo')
    fecha_limite = Column(Date)
    creado_en = Column(DateTime, default=datetime.utcnow)
    propietario_id = Column(Integer, ForeignKey('usuarios.id'))
    propietario = relationship('Usuario', back_populates='proyectos')
    tareas = relationship('Tarea', back_populates='proyecto',
    cascade='all, delete-orphan')

    @property
    def progreso(self):
        total = len(self.tareas)
        if total == 0: return 0
        completadas = sum(1 for t in self.tareas if t.estado == 'completada')
        return round(completadas / total * 100)

class Tarea(Base):
    __tablename__ = 'tareas'
    id = Column(Integer, primary_key=True)
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text)
    prioridad = Column(String(20), default='media')
    estado = Column(String(20), default='pendiente')
    fecha_limite = Column(Date)
    creado_en = Column(DateTime, default=datetime.utcnow)
    proyecto_id = Column(Integer, ForeignKey('proyectos.id'))
    asignado_id = Column(Integer, ForeignKey('usuarios.id'), nullable=True)
    proyecto = relationship('Proyecto', back_populates='tareas')
    etiquetas = relationship('Etiqueta', secondary=tarea_etiqueta,
        back_populates='tareas')

class Etiqueta(Base):
    __tablename__ = 'etiquetas'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(50), unique=True, nullable=False)
    color = Column(String(7), default='#3498db')
    tareas = relationship('Tarea', secondary=tarea_etiqueta,
        back_populates='etiquetas')
