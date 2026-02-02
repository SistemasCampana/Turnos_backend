from flaskr import db
from flask import Blueprint, jsonify, request
from datetime import datetime
from flaskr.modelos.modelos import Turno, TurnoSchema, EstadoTurno, Usuario
from flask_jwt_extended import jwt_required, get_jwt_identity
from flaskr.controllers.login_controller import admin_required 

# Definición del Blueprint
turno_bp = Blueprint('turno_bp', __name__)
turno_schema = TurnoSchema()
turnos_schema = TurnoSchema(many=True)

@turno_bp.route('/turnos/', methods=['POST', 'OPTIONS'])
@jwt_required()
def crear_turno():
    # Manejo explícito de peticiones OPTIONS para evitar errores de CORS
    if request.method == 'OPTIONS':
        return '', 200
           
    try:
        data = request.get_json()
        nombre_cliente = data.get("nombre_cliente")
        bodega = data.get("bodega")
        sede = data.get("sede")

        if not nombre_cliente or not bodega or not sede:
            return jsonify({"error": "Faltan datos obligatorios"}), 400

        # Lógica para generar el número de turno
        ultimo_turno = Turno.query.filter_by(sede=sede).order_by(Turno.id.desc()).first()
        if ultimo_turno:
            try:
                numero_actual = int(ultimo_turno.numero[1:])
                nuevo_numero = f"A{str(numero_actual + 1).zfill(3)}"
            except (ValueError, TypeError):
                nuevo_numero = "A001"
        else:
            nuevo_numero = "A001"

        nuevo_turno = Turno(
            numero=nuevo_numero,
            nombre_cliente=nombre_cliente,
            bodega=bodega,
            sede=sede,
            estado=EstadoTurno.llamado.value,
            modulo=1
        )
        
        db.session.add(nuevo_turno)
        db.session.commit()
        
        return jsonify(turno_schema.dump(nuevo_turno)), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error en el servidor: {str(e)}")
        return jsonify({"error": "Error interno al crear el turno"}), 500

@turno_bp.route('/turnos/ultimo', methods=['GET'])
def obtener_ultimo():
    sede_solicitada = request.args.get('sede')
    if not sede_solicitada:
        return jsonify({"error": "Debe especificar una sede"}), 400

    turno = Turno.query.filter_by(
        estado=EstadoTurno.llamado.value, 
        sede=sede_solicitada
    ).order_by(Turno.id.desc()).first()
    
    return jsonify(turno_schema.dump(turno)) if turno else jsonify({}), 200

# --- RUTA PARA EL INFORME CORREGIDA ---
@turno_bp.route('/turnos/informe/<fecha>', methods=['GET'])
@jwt_required()
def obtener_informe(fecha):
    try:
        # IMPORTANTE: Cambiamos 'fecha_creacion' por 'creado_en' para coincidir con tu modelo real
        # Esto evitará el Error 500 en Render
        turnos = Turno.query.filter(
            db.func.cast(Turno.creado_en, db.Date) == fecha
        ).all()

        return jsonify({
            "fecha": fecha,
            "total_turnos": len(turnos),
            "detalle_turnos": turnos_schema.dump(turnos)
        }), 200
    except Exception as e:
        print(f"Error en informe: {str(e)}")
        return jsonify({"error": "No se pudo generar el informe"}), 500

@turno_bp.route('/turnos/reiniciar', methods=['POST'])
@admin_required 
def reiniciar_turnos():
    try:
        Turno.query.delete()
        db.session.commit()
        return jsonify({"mensaje": "Base de datos reiniciada"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500