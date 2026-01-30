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
    __tablename__ = 'turnos' # Esta será la tabla única en pgAdmin
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    numero = db.Column(db.String(10), nullable=False)
    nombre_cliente = db.Column(db.String(100), nullable=True)
    bodega = db.Column(db.String(100), nullable=True)   
    modulo = db.Column(db.Integer, nullable=True)
    sede = db.Column(db.String(50), nullable=True, default="Paloquemao")
    estado = db.Column(db.String(20), default=EstadoTurno.esperando.value, nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

class Usuario(db.Model):
    __tablename__ = 'usuarios' # Esta será la tabla única en pgAdmin
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=True) 
    sede = db.Column(db.String(100), nullable=True)
    rol = db.Column(db.String(50), nullable=True, default="visor") 

    def set_password(self, password):
        """Genera un hash seguro para la contraseña."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica la contraseña contra el hash almacenado."""
        # Eliminamos la comparación de texto plano para usar solo hashes seguros
        return check_password_hash(self.password_hash, password)

# --- ESQUEMAS DE SERIALIZACIÓN ---
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