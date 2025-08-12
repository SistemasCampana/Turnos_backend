from marshmallow import fields
from flaskr import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
import enum

# ========================
# Enum para los estados del turno
# ========================
class EstadoTurno(enum.Enum):
    esperando = "esperando"
    llamado = "llamado"
    atendido = "atendido"

# ========================
# Modelo de Turnos
# ========================
class Turno(db.Model):
    __tablename__ = 'turnos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    numero = db.Column(db.String(10), nullable=False)
    modulo = db.Column(db.Integer, nullable=True)
    estado = db.Column(
        db.Enum(EstadoTurno, name="estado_turno", native_enum=False),
        default=EstadoTurno.esperando,
        nullable=False
    )
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Turno {self.numero} - Módulo {self.modulo} - Estado {self.estado.value}>'

# ========================
# Modelo de Usuarios
# ========================
class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        """Guarda la contraseña hasheada."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica si la contraseña ingresada coincide."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Usuario {self.username}>'

# ========================
# SERIALIZADORES
# ========================
class TurnoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Turno
        include_relationships = True
        load_instance = True

    # Para que en JSON salga como string
    estado = fields.Method("get_estado", deserialize="load_estado")

    def get_estado(self, obj):
        return obj.estado.value if obj.estado else None

    def load_estado(self, value):
        return EstadoTurno(value)

class UsuarioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario
        load_instance = True

