# flaskr/controllers/turno_controller.py
from flaskr import db
from flask import Blueprint, jsonify, request
from flaskr.modelos import Turno, TurnoSchema, EstadoTurno

turno_bp = Blueprint('turnos', __name__)
turno_schema = TurnoSchema()
turnos_schema = TurnoSchema(many=True)

def opciones_cors():
    response = jsonify({})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    return response

@turno_bp.route('/', methods=['POST', 'OPTIONS'])
def crear_turno():
    if request.method == 'OPTIONS':
        return opciones_cors()

    data = request.get_json()
    nombre_cliente = data.get("nombre_cliente")
    bodega = data.get("bodega")

    if not nombre_cliente or not bodega:
        return jsonify({"error": "El nombre del cliente y la bodega son obligatorios"}), 400

    # Obtener último turno para calcular el número
    ultimo_turno = Turno.query.order_by(Turno.id.desc()).first()

    if ultimo_turno:
        numero_actual = int(ultimo_turno.numero[1:])
        nuevo_numero = "A" + str(numero_actual + 1).zfill(3)
    else:
        nuevo_numero = "A001"

    # Crear turno con cliente y bodega
    nuevo_turno = Turno(
        numero=nuevo_numero,
        nombre_cliente=nombre_cliente,
        bodega=bodega,
        estado=EstadoTurno.esperando
    )
    db.session.add(nuevo_turno)
    db.session.commit()

    return turno_schema.jsonify(nuevo_turno), 201

@turno_bp.route('/ultimo', methods=['GET', 'OPTIONS'])
def obtener_ultimo():
    if request.method == 'OPTIONS':
        return opciones_cors()

    turno = Turno.query.filter_by(estado=EstadoTurno.llamado).order_by(Turno.id.desc()).first()
    if turno:
        return jsonify(turno_schema.dump(turno))
    else:
        return jsonify({})

@turno_bp.route('/siguiente', methods=['POST', 'OPTIONS'])
def llamar_siguiente():
    if request.method == 'OPTIONS':
        return opciones_cors()

    modulo = request.json.get('modulo', 1)
    turno = Turno.query.filter_by(estado=EstadoTurno.esperando).order_by(Turno.id.asc()).first()

    if turno:
        turno.estado = EstadoTurno.llamado
        turno.modulo = modulo
        db.session.commit()
        return jsonify(turno_schema.dump(turno))

    return jsonify({'mensaje': 'No hay turnos disponibles'}), 404

@turno_bp.route('/reiniciar', methods=['POST'])
def reiniciar_turnos():
    try:
        Turno.query.delete()
        db.session.commit()
        return jsonify({"mensaje": "Turnos reiniciados correctamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
