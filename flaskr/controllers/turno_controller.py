from flask import Blueprint, jsonify, request
from flaskr.db import get_connection

turno_bp = Blueprint('turnos', __name__)

@turno_bp.route('/', methods=['POST'])
def crear_turno():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT numero FROM turnos ORDER BY id DESC LIMIT 1")
    last = cursor.fetchone()
    
    if last:
        numero_actual = int(last['numero'][1:])
        nuevo_numero = "A" + str(numero_actual + 1).zfill(3)
    else:
        nuevo_numero = "A001"


    cursor.execute("INSERT INTO turnos (numero, estado) VALUES (%s, %s)", (nuevo_numero, 'esperando'))
    conn.commit()   
    conn.close()
    
    return jsonify({'numero': nuevo_numero})

@turno_bp.route('/ultimo', methods=['GET'])
def obtener_ultimo():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM turnos WHERE estado = 'llamado' ORDER BY id DESC LIMIT 1")
    turno = cursor.fetchone()
    conn.close()
    return jsonify(turno if turno else {})

@turno_bp.route('/siguiente', methods=['POST'])
def llamar_siguiente():
    modulo = request.json.get('modulo', 1)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM turnos WHERE estado = 'esperando' ORDER BY id ASC LIMIT 1")
    turno = cursor.fetchone()

    if turno:
        cursor.execute("UPDATE turnos SET estado = 'llamado', modulo = %s WHERE id = %s", (modulo, turno['id']))
        conn.commit()
        turno['modulo'] = modulo
        turno['estado'] = 'llamado'
        
    conn.close()
    return jsonify(turno if turno else {'mensaje': 'No hay turnos disponibles'})







