from flaskr import db
from flask import Blueprint, jsonify, request
from datetime import datetime
import pytz 
from flaskr.modelos.modelos import Turno, TurnoSchema, EstadoTurno
# Importamos cross_origin para manejar CORS de forma más limpia si es necesario
from flask_cors import cross_origin

turno_bp = Blueprint('turnos', __name__)
turno_schema = TurnoSchema()
turnos_schema = TurnoSchema(many=True)

# --- RUTAS PRINCIPALES ---

@turno_bp.route('/', methods=['POST'])
def crear_turno():
    try:
        data = request.get_json()
        nombre_cliente = data.get("nombre_cliente")
        bodega = data.get("bodega")
        sede = data.get("sede")

        if not nombre_cliente or not bodega or not sede:
            return jsonify({"error": "El nombre, la bodega y la sede son obligatorios"}), 400

        # Buscamos el último número basado estrictamente en la sede
        ultimo_turno = Turno.query.filter_by(sede=sede).order_by(Turno.id.desc()).first()

        if ultimo_turno:
            try:
                # Extraemos el número después de la 'A' (ej: A005 -> 5)
                numero_actual = int(ultimo_turno.numero[1:])
                nuevo_numero = f"A{str(numero_actual + 1).zfill(3)}"
            except ValueError:
                nuevo_numero = "A001"
        else:
            nuevo_numero = "A001"

        nuevo_turno = Turno(
            numero=nuevo_numero,
            nombre_cliente=nombre_cliente,
            bodega=bodega,
            sede=sede,
            estado=EstadoTurno.llamado.value, # Se crea como llamado para que aparezca en pantalla
            modulo=1
        )
        
        db.session.add(nuevo_turno)
        db.session.commit()

        return jsonify(turno_schema.dump(nuevo_turno)), 201

    except Exception as e:
        db.session.rollback()  
        return jsonify({"error": str(e)}), 500


@turno_bp.route('/ultimo', methods=['GET'])
def obtener_ultimo():
    # Capturamos la sede de los parámetros de la URL
    sede_solicitada = request.args.get('sede')

    if not sede_solicitada:
        return jsonify({"error": "Debe especificar una sede"}), 400

    # Filtramos por estado LLAMADO y por SEDE específica
    turno = Turno.query.filter_by(
        estado=EstadoTurno.llamado.value, 
        sede=sede_solicitada
    ).order_by(Turno.id.desc()).first()
    
    if turno:
        return jsonify(turno_schema.dump(turno))
    
    return jsonify({}), 200


@turno_bp.route('/siguiente', methods=['POST'])
def llamar_siguiente():
    data = request.get_json()
    modulo = data.get('modulo', 1)
    sede = data.get('sede')
    
    if not sede:
        return jsonify({"error": "Sede no especificada"}), 400

    # Busca el primer turno en espera de ESA sede
    turno = Turno.query.filter_by(
        estado=EstadoTurno.esperando.value,
        sede=sede
    ).order_by(Turno.id.asc()).first()

    if turno:
        turno.estado = EstadoTurno.llamado.value
        turno.modulo = modulo
        db.session.commit()
        return jsonify(turno_schema.dump(turno))

    return jsonify({'mensaje': 'No hay turnos disponibles para esta sede'}), 404


@turno_bp.route('/reiniciar', methods=['POST'])
def reiniciar_turnos():
    try:
        # Nota: Esto borra TODO. Si quieres borrar solo una sede, agrega .filter_by(sede=...)
        Turno.query.delete()
        db.session.commit()
        return jsonify({"mensaje": "Turnos reiniciados correctamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# --- UTILIDADES E INFORMES ---

def serializar_turno_para_informe(turno):
    hora_generacion = "N/A"
    zona_utc = pytz.utc
    zona_bogota = pytz.timezone('America/Bogota') 
    
    try:
        if hasattr(turno, 'creado_en') and turno.creado_en:
            # Aseguramos que sea consciente de UTC y convertimos
            utc_dt = zona_utc.localize(turno.creado_en) if turno.creado_en.tzinfo is None else turno.creado_en
            local_dt = utc_dt.astimezone(zona_bogota)
            hora_generacion = local_dt.strftime('%I:%M %p') 
    except Exception:
        pass 

    return {
        'id': turno.id,
        'numero': turno.numero,
        'nombre_cliente': turno.nombre_cliente,
        'bodega': turno.bodega,
        'sede': turno.sede,
        'estado': turno.estado,
        'modulo': turno.modulo,
        'hora_generacion': hora_generacion, 
    }

@turno_bp.route('/informe/<string:fecha_str>', methods=['GET'])
def generar_informe(fecha_str):
    try:
        fecha_a_buscar = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        # Llamamos al método del modelo que ya creaste
        turnos_del_dia = Turno.obtener_turnos_por_fecha(fecha_a_buscar)

        turnos_detalle = [serializar_turno_para_informe(t) for t in turnos_del_dia]
        
        return jsonify({
            "fecha": fecha_str,
            "total_turnos": len(turnos_del_dia),
            "detalle_turnos": turnos_detalle
        }), 200

    except ValueError:
        return jsonify({"error": "Formato de fecha inválido. Use YYYY-MM-DD"}), 400
    except Exception as e:
        return jsonify({"error": f"Error al generar el informe: {str(e)}"}), 500




# from flaskr import db
# from flask import Blueprint, jsonify, request
# # 🚨 Agregamos datetime para el manejo de la fecha en el informe
# from datetime import datetime
# import pytz 
# from flaskr.modelos.modelos import Turno, TurnoSchema, EstadoTurno
# # Importamos la función func de SQLAlchemy para trabajar con fechas en la base de datos
# # from sqlalchemy import func

# turno_bp = Blueprint('turnos', __name__)
# turno_schema = TurnoSchema()
# turnos_schema = TurnoSchema(many=True)

# def opciones_cors():
#     response = jsonify({})
#     response.headers.add("Access-Control-Allow-Origin", "*")
#     response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
#     response.headers.add("Access-Control-Allow-Headers", "Content-Type")
#     return response

# @turno_bp.route('/', methods=['POST', 'OPTIONS'])
# def crear_turno():
#     if request.method == 'OPTIONS':
#         return opciones_cors()

#     try:
#         data = request.get_json()
#         nombre_cliente = data.get("nombre_cliente")
#         bodega = data.get("bodega")
#         sede = data.get("sede")

#         if not nombre_cliente or not bodega:
#             return jsonify({"error": "El nombre del cliente y la bodega son obligatorios"}), 400

#         # Obtener último turno para calcular el número
#         ultimo_turno = Turno.query.order_by(Turno.id.desc()).first()

#         if ultimo_turno:
#             numero_actual = int(ultimo_turno.numero[1:])
#             nuevo_numero = "A" + str(numero_actual + 1).zfill(3)
#         else:
#             nuevo_numero = "A001"

#         # 🔹 Crear turno con cliente y bodega, ya en estado "llamado"
#         nuevo_turno = Turno(
#             numero=nuevo_numero,
#             nombre_cliente=nombre_cliente,
#             bodega=bodega,
#             sede=sede,
#             estado=EstadoTurno.llamado.value,  
#             modulo=1,
#             # NOTA: Se asume que 'fecha_creacion' se establece automáticamente 
#             # en el modelo de la base de datos al crearse.
#         )
#         db.session.add(nuevo_turno)
#         db.session.commit()

#         return jsonify(turno_schema.dump(nuevo_turno)), 201

#     except Exception as e:
#         db.session.rollback()  # Por si la BD falló
#         return jsonify({"error": str(e)}), 500


# @turno_bp.route('/ultimo', methods=['GET', 'OPTIONS'])
# def obtener_ultimo():
#     if request.method == 'OPTIONS':
#         return opciones_cors()

#     turno = Turno.query.filter_by(estado=EstadoTurno.llamado.value).order_by(Turno.id.desc()).first()
#     if turno:
#         return jsonify(turno_schema.dump(turno))
#     else:
#         return jsonify({})

# @turno_bp.route('/siguiente', methods=['POST', 'OPTIONS'])
# def llamar_siguiente():
#     if request.method == 'OPTIONS':
#         return opciones_cors()

#     modulo = request.json.get('modulo', 1)
#     turno = Turno.query.filter_by(estado=EstadoTurno.esperando.value).order_by(Turno.id.asc()).first()

#     if turno:
#         turno.estado = EstadoTurno.llamado.value
#         turno.modulo = modulo
#         db.session.commit()
#         return jsonify(turno_schema.dump(turno))

#     return jsonify({'mensaje': 'No hay turnos disponibles'}), 404

# @turno_bp.route('/reiniciar', methods=['POST'])
# def reiniciar_turnos():
#     try:
#         Turno.query.delete()
#         db.session.commit()
#         return jsonify({"mensaje": "Turnos reiniciados correctamente"}), 200
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"error": str(e)}), 500


# # --- NUEVA FUNCIÓN DE UTILIDAD: Serializa el turno y formatea la hora ---
# def serializar_turno_para_informe(turno):
#     """
#     Convierte un objeto Turno a un diccionario, convirtiendo el tiempo UTC 
#     al huso horario de America/Bogota para mostrar la hora local.
#     """
#     hora_generacion = "N/A" # Valor por defecto
    
#     # 🚨 PASO CLAVE 2: Configuramos las zonas horarias
#     zona_utc = pytz.utc
#     zona_bogota = pytz.timezone('America/Bogota') 
    
#     try:
#         if hasattr(turno, 'creado_en') and isinstance(getattr(turno, 'creado_en'), datetime):
            
#             # 1. Hacer el datetime consciente de que está en UTC
#             utc_dt = zona_utc.localize(turno.creado_en)
            
#             # 2. Convertir el tiempo de UTC a la hora de Bogotá
#             local_dt = utc_dt.astimezone(zona_bogota)

#             # 3. Formatear la hora local de Bogotá (usando AM/PM: %I:%M %p)
#             hora_generacion = local_dt.strftime('%I:%M %p') 
#     except Exception:
#         # En caso de error, la hora_generacion se queda en "N/A"
#         pass 

#     # Retorna el diccionario con todos los campos necesarios para el frontend
#     return {
#         'id': turno.id,
#         'numero': turno.numero,
#         'nombre_cliente': turno.nombre_cliente,
#         'bodega': turno.bodega,
#         'estado': turno.estado,
#         'modulo': turno.modulo,
#         'hora_generacion': hora_generacion, 
#     }


# # 📊 NUEVA FUNCIÓN PARA GENERAR EL INFORME POR FECHA
# @turno_bp.route('/informe/<string:fecha_str>', methods=['GET', 'OPTIONS'])
# def generar_informe(fecha_str):
#     if request.method == 'OPTIONS':
#         return opciones_cors()
    
#     try:
#         # Convertir la string de fecha (ej: '2025-12-05') a un objeto datetime.date
#         fecha_a_buscar = datetime.strptime(fecha_str, '%Y-%m-%d').date()

#         # 🛑 ACTUALIZACIÓN CLAVE: Usamos la función de SQLAlchemy para filtrar por la parte de fecha
#         # Llama a tu método (asumiendo que está en el modelo) o consulta directamente:
#         # turnos_del_dia = Turno.obtener_turnos_por_fecha(fecha_a_buscar)
        
#         # Como no puedo ver tu método, usaré la consulta directa que es más común:
#         turnos_del_dia = Turno.obtener_turnos_por_fecha(fecha_a_buscar)

#         # 1. Obtener la lista detallada de turnos
#         # 🛑 CAMBIO CLAVE: Usamos la función manual para incluir 'hora_generacion'
#         turnos_detalle = [
#             serializar_turno_para_informe(t)
#             for t in turnos_del_dia
#         ]
        
#         # 2. Calcular el total de turnos
#         total_turnos = len(turnos_del_dia)

#         # 3. Formato del informe de respuesta
#         informe = {
#             "fecha": fecha_str,
#             "total_turnos": total_turnos,
#             "detalle_turnos": turnos_detalle
#         }

#         return jsonify(informe), 200

#     except ValueError:
#         # Esto ocurre si la fecha_str no tiene el formato correcto '%Y-%m-%d'
#         return jsonify({"error": "Formato de fecha inválido. Use YYYY-MM-DD"}), 400
#     except Exception as e:
#         return jsonify({"error": f"Error al generar el informe: {str(e)}"}), 500

