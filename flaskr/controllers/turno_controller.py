# flaskr/controllers/turno_controller.py
from flaskr import db
from flask import Blueprint, jsonify, request
from flaskr.modelos import Turno, TurnoSchema

turno_bp = Blueprint('turnos', __name__)
turno_schema = TurnoSchema()
turnos_schema = TurnoSchema(many=True)

@turno_bp.route('/', methods=['POST'])
def crear_turno():
    # Obtener el último turno creado
    ultimo_turno = Turno.query.order_by(Turno.id.desc()).first()

    if ultimo_turno:
        numero_actual = int(ultimo_turno.numero[1:])
        nuevo_numero = "A" + str(numero_actual + 1).zfill(3)
    else:
        nuevo_numero = "A001"

    # Crear nuevo turno
    nuevo_turno = Turno(numero=nuevo_numero, estado='esperando')
    db.session.add(nuevo_turno)
    db.session.commit()

    return jsonify({'numero': nuevo_numero}), 201

@turno_bp.route('/ultimo', methods=['GET'])
def obtener_ultimo():
    turno = Turno.query.filter_by(estado='llamado').order_by(Turno.id.desc()).first()
    return turno_schema.jsonify(turno) if turno else jsonify({})

@turno_bp.route('/siguiente', methods=['POST'])
def llamar_siguiente():
    modulo = request.json.get('modulo', 1)

    turno = Turno.query.filter_by(estado='esperando').order_by(Turno.id.asc()).first()

    if turno:
        turno.estado = 'llamado'
        turno.modulo = modulo
        db.session.commit()
        return turno_schema.jsonify(turno)

    return jsonify({'mensaje': 'No hay turnos disponibles'}), 404
