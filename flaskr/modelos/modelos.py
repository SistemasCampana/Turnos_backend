from marshmallow import fields
from flaskr import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
import enum

class EstadoTurno(enum.Enum):
    esperando = "esperando"
    llamado = "llamado"
    atendido = "atendido"

class Turno(db.Model):  
    __tablename__ = 'turnos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    numero = db.Column(db.String(10), nullable=False)
    nombre_cliente = db.Column(db.String(100), nullable=True)
    bodega = db.Column(db.String(100), nullable=True)   
    modulo = db.Column(db.Integer, nullable=True)
    sede = db.Column(db.String(50), nullable=False, default="Paloquemao")
    # Ampliamos a 20 para evitar errores si agregas estados más largos
    estado = db.Column(db.String(20), default=EstadoTurno.esperando.value, nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def obtener_turnos_por_fecha(fecha_a_buscar):
        return Turno.query.filter(
            db.func.date(Turno.creado_en) == fecha_a_buscar
        ).order_by(Turno.id.asc()).all()

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    sede = db.Column(db.String(50), nullable=False, default="Paloquemao")
    # Ampliamos a 50 para soportar 'administrador', 'emergencia', etc.
    rol = db.Column(db.String(50), nullable=False, default="visor") 

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Esquemas para Marshmallow
class TurnoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Turno
        include_relationships = True
        load_instance = True
    estado = fields.String()

class UsuarioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario
        load_instance = True