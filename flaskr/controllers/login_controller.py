from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, verify_jwt_in_request
from flaskr.modelos.modelos import Usuario, db
from flask_cors import CORS
import datetime
from functools import wraps

login_bp = Blueprint('login', __name__)
# El CORS ya se maneja de forma global en app.py, pero lo mantenemos por seguridad local
CORS(login_bp)

# --- DECORADOR DE SEGURIDAD PARA EL ADMIN ---
def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            identity = get_jwt_identity()
            # Buscamos por ID (que viene del JWT)
            usuario = Usuario.query.get(int(identity))
            if not usuario or usuario.rol != 'administrador':
                return jsonify({"msg": "Acceso restringido: Solo el administrador puede realizar esta acción"}), 403
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({"msg": "Token inválido o expirado", "error": str(e)}), 401
    return wrapper

@login_bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return jsonify({"msg": "ok"}), 200

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"msg": "Usuario y contraseña son obligatorios"}), 400

    # Búsqueda de usuario ignorando mayúsculas/minúsculas para evitar errores de tipeo
    usuario = Usuario.query.filter_by(username=username).first()

    if not usuario or not usuario.check_password(password):
        return jsonify({"msg": "Usuario o contraseña incorrectos"}), 401

    # Creamos el token usando el ID como identidad
    access_token = create_access_token(
        identity=str(usuario.id), 
        expires_delta=datetime.timedelta(hours=8) # Tiempo extendido para jornada laboral
    )

    return jsonify({
        "access_token": access_token,
        "rol": usuario.rol,
        "username": usuario.username,
        "sede": usuario.sede
    }), 200

@login_bp.route('/usuarios/registro', methods=['POST', 'OPTIONS'])
@admin_required 
def registro():
    if request.method == 'OPTIONS':
        return jsonify({"msg": "ok"}), 200

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    rol = data.get('rol', 'operador') # Valor por defecto
    sede = data.get('sede', 'Paloquemao')

    if not username or not password:
        return jsonify({"msg": "Faltan datos obligatorios"}), 400

    if Usuario.query.filter_by(username=username).first():
        return jsonify({"msg": "El nombre de usuario ya está en uso"}), 400

    try:
        nuevo_usuario = Usuario(username=username, rol=rol, sede=sede)
        nuevo_usuario.set_password(password)
        db.session.add(nuevo_usuario)
        db.session.commit()
        return jsonify({"msg": f"Usuario {username} creado exitosamente"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Error en el servidor: {str(e)}"}), 500