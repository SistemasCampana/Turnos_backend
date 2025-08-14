# flaskr/controllers/turno_controller.py
from flaskr import db
from flask import Blueprint, jsonify, request, make_response
from flaskr.modelos import Turno, TurnoSchema

turno_bp = Blueprint('turnos', __name__)
turno_schema = TurnoSchema()
turnos_schema = TurnoSchema(many=True)

# Función helper para respuesta OPTIONS
def opciones_cors():
    response = make_response('', 204)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@turno_bp.route('/', methods=['POST', 'OPTIONS'])
def crear_turno():
    if request.method == 'OPTIONS':
        return opciones_cors()

    ultimo_turno = Turno.query.order_by(Turno.id.desc()).first()

    if ultimo_turno:
        numero_actual = int(ultimo_turno.numero[1:])
        nuevo_numero = "A" + str(numero_actual + 1).zfill(3)
    else:
        nuevo_numero = "A001"

    nuevo_turno = Turno(numero=nuevo_numero, estado='esperando')
    db.session.add(nuevo_turno)
    db.session.commit()

    return jsonify({'numero': nuevo_numero}), 201

@turno_bp.route('/ultimo', methods=['GET', 'OPTIONS'])
def obtener_ultimo():
    if request.method == 'OPTIONS':
        return opciones_cors()

    turno = Turno.query.filter_by(estado='llamado').order_by(Turno.id.desc()).first()
    return turno_schema.jsonify(turno) if turno else jsonify({})

@turno_bp.route('/siguiente', methods=['POST', 'OPTIONS'])
def llamar_siguiente():
    if request.method == 'OPTIONS':
        return opciones_cors()

    modulo = request.json.get('modulo', 1)

    turno = Turno.query.filter_by(estado='esperando').order_by(Turno.id.asc()).first()

    if turno:
        turno.estado = 'llamado'
        turno.modulo = modulo
        db.session.commit()
        return turno_schema.jsonify(turno)

    return jsonify({'mensaje': 'No hay turnos disponibles'}), 404
