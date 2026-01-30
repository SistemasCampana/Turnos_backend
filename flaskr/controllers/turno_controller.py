from flaskr import db
from flask import Blueprint, jsonify, request
from datetime import datetime
from flaskr.modelos.modelos import Turno, TurnoSchema, EstadoTurno
from flaskr.controllers.login_controller import admin_required 

turno_bp = Blueprint('turno_bp', __name__)
turno_schema = TurnoSchema()
turnos_schema = TurnoSchema(many=True)

# ... (tus rutas de crear_turno y obtener_ultimo se mantienen igual)

@turno_bp.route('/turnos/informe/<fecha>', methods=['GET'])
def obtener_informe(fecha):
    try:
        # PostgreSQL: Filtramos usando el nombre exacto de tu modelo: 'creado_en'
        turnos = Turno.query.filter(
            db.func.cast(Turno.creado_en, db.Date) == fecha
        ).all()

        return jsonify({
            "fecha": fecha,
            "total_turnos": len(turnos),
            "detalle_turnos": turnos_schema.dump(turnos)
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error en el servidor: {str(e)}"}), 500

@turno_bp.route('/turnos/reiniciar', methods=['POST'])
@admin_required 
def reiniciar_turnos():
    try:
        Turno.query.delete()
        db.session.commit()
        return jsonify({"mensaje": "Turnos reiniciados correctamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500