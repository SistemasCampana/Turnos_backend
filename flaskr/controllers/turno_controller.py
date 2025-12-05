# flaskr/controllers/turno_controller.py
from flaskr import db
from flask import Blueprint, jsonify, request
# 🚨 Agregamos datetime para el manejo de la fecha en el informe
from datetime import datetime 
from flaskr.modelos.modelos import Turno, TurnoSchema, EstadoTurno

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

    try:
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

        # 🔹 Crear turno con cliente y bodega, ya en estado "llamado"
        nuevo_turno = Turno(
            numero=nuevo_numero,
            nombre_cliente=nombre_cliente,
            bodega=bodega,
            estado=EstadoTurno.llamado.value,  
            modulo=1  
        )
        db.session.add(nuevo_turno)
        db.session.commit()

        return jsonify(turno_schema.dump(nuevo_turno)), 201

    except Exception as e:
        db.session.rollback()  # Por si la BD falló
        return jsonify({"error": str(e)}), 500


@turno_bp.route('/ultimo', methods=['GET', 'OPTIONS'])
def obtener_ultimo():
    if request.method == 'OPTIONS':
        return opciones_cors()

    turno = Turno.query.filter_by(estado=EstadoTurno.llamado.value).order_by(Turno.id.desc()).first()
    if turno:
        return jsonify(turno_schema.dump(turno))
    else:
        return jsonify({})

@turno_bp.route('/siguiente', methods=['POST', 'OPTIONS'])
def llamar_siguiente():
    if request.method == 'OPTIONS':
        return opciones_cors()

    modulo = request.json.get('modulo', 1)
    turno = Turno.query.filter_by(estado=EstadoTurno.esperando.value).order_by(Turno.id.asc()).first()

    if turno:
        turno.estado = EstadoTurno.llamado.value
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


# 📊 NUEVA FUNCIÓN PARA GENERAR EL INFORME POR FECHA
@turno_bp.route('/informe/<string:fecha_str>', methods=['GET', 'OPTIONS'])
def generar_informe(fecha_str):
    if request.method == 'OPTIONS':
        return opciones_cors()
    
    try:
        # Convertir la string de fecha (ej: '2025-12-05') a un objeto datetime.date
        fecha_a_buscar = datetime.strptime(fecha_str, '%Y-%m-%d').date()

        # Llama al método estático que debe estar definido en modelos.py (Clase Turno)
        turnos_del_dia = Turno.obtener_turnos_por_fecha(fecha_a_buscar)

        # 1. Obtener la lista detallada de turnos
        turnos_detalle = turnos_schema.dump(turnos_del_dia)
        
        # 2. Calcular el total de turnos
        total_turnos = len(turnos_del_dia)

        # 3. Formato del informe de respuesta
        informe = {
            "fecha": fecha_str,
            "total_turnos": total_turnos,
            "detalle_turnos": turnos_detalle
        }

        return jsonify(informe), 200

    except ValueError:
        # Esto ocurre si la fecha_str no tiene el formato correcto '%Y-%m-%d'
        return jsonify({"error": "Formato de fecha inválido. Use YYYY-MM-DD"}), 400
    except Exception as e:
        return jsonify({"error": f"Error al generar el informe: {str(e)}"}), 500