from marshmallow import fields
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import enum

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

db = SQLAlchemy()

class Turno(db.Model):
    __tablename__ = 'turnos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    numero = db.Column(db.String(10), nullable=False)
    modulo = db.Column(db.Integer, nullable=True)
    estado = db.Column(db.Enum('esperando', 'llamado', 'atendido', name='estado_turno'), default='esperando', nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Turno {self.numero} - Módulo {self.modulo} - Estado {self.estado}>'

#SERIALIZACION

class TurnoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Turno
        include_relationships = True
        load_instance = True


