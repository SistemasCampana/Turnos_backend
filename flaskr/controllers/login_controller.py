# flaskr/controllers/login_controller.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
# CORRECCIÓN: Importación específica desde la carpeta modelos
from flaskr.modelos.modelos import Usuario 
import datetime

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"msg": "Usuario y contraseña son obligatorios"}), 400

    # Busca al usuario en la base de datos
    usuario = Usuario.query.filter_by(username=username).first()

    # CORRECCIÓN: Usamos el método check_password definido en tu modelo
    # Quitamos la verificación de 'usuario.password_hash' aquí porque check_password ya lo hace internamente
    if not usuario or not usuario.check_password(password):
        return jsonify({"msg": "Credenciales inválidas"}), 401

    # Crear token de acceso
    access_token = create_access_token(
        identity=str(usuario.id), # Es mejor práctica que la identidad sea un string
        expires_delta=datetime.timedelta(hours=1)
    )

    # Devolvemos el rol y el username para que el frontend (React) los use
    return jsonify({
        "access_token": access_token,
        "rol": usuario.rol,       # Esto devolverá 'visor' o 'admin' según la DB
        "username": usuario.username
    }), 200




# # flaskr/controllers/login_controller.py
# from flask import Blueprint, request, jsonify
# from flask_jwt_extended import create_access_token
# from flaskr.modelos import Usuario
# import datetime

# login_bp = Blueprint('login', __name__)

# @login_bp.route('/login', methods=['POST'])
# def login():
#     data = request.get_json()

#     username = data.get('username')
#     password = data.get('password')

#     if not username or not password:
#         return jsonify({"msg": "Usuario y contraseña son obligatorios"}), 400

#     usuario = Usuario.query.filter_by(username=username).first()

#     # Blindaje: verifica usuario y contraseña
#     if not usuario or not usuario.password_hash or not usuario.check_password(password):
#         return jsonify({"msg": "Credenciales inválidas"}), 401

#     # Crear token
#     access_token = create_access_token(
#         identity=usuario.id,
#         expires_delta=datetime.timedelta(hours=1)
#     )

#     # IMPORTANTE: Devolvemos el rol y el username junto al token
#     return jsonify({
#         "access_token": access_token,
#         "rol": usuario.rol,       # Asegúrate de tener la columna 'rol' en tu modelo
#         "username": usuario.username
#     }), 200