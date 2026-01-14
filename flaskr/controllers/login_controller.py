from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from flaskr.modelos.modelos import Usuario, db # Importamos db para guardar
from flask_cors import CORS
import datetime

login_bp = Blueprint('login', __name__)

# Aplicamos CORS directamente al blueprint para resolver el error de preflight
CORS(login_bp)

@login_bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return jsonify({"msg": "ok"}), 200

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"msg": "Usuario y contraseña son obligatorios"}), 400

    usuario = Usuario.query.filter_by(username=username).first()

    if not usuario or not usuario.check_password(password):
        return jsonify({"msg": "Credenciales inválidas"}), 401

    access_token = create_access_token(
        identity=str(usuario.id),
        expires_delta=datetime.timedelta(hours=1)
    )

    return jsonify({
        "access_token": access_token,
        "rol": usuario.rol,
        "username": usuario.username,
        "sede": usuario.sede
    }), 200

# NUEVA RUTA: Registro de usuarios (la que fallaba en tu imagen)
@login_bp.route('/usuarios/registro', methods=['POST', 'OPTIONS'])
def registro():
    # Manejo explícito de la consulta de seguridad del navegador
    if request.method == 'OPTIONS':
        return jsonify({"msg": "ok"}), 200

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    rol = data.get('rol')
    sede = data.get('sede', 'Paloquemao') # Valor por defecto si no llega

    if not username or not password:
        return jsonify({"msg": "Faltan datos obligatorios"}), 400

    # Verificar si el usuario ya existe
    if Usuario.query.filter_by(username=username).first():
        return jsonify({"msg": "El usuario ya existe"}), 400

    try:
        # Crear el nuevo usuario usando el método de tu modelo para hashear la clave
        nuevo_usuario = Usuario(username=username, rol=rol, sede=sede)
        nuevo_usuario.set_password(password) # Asumiendo que tu modelo tiene set_password
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        return jsonify({"msg": "Usuario creado exitosamente"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Error al crear usuario: {str(e)}"}), 500