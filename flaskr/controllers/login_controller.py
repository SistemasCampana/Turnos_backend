# flaskr/controllers/login_controller.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from flaskr.modelos import Usuario
from flaskr import db
import datetime

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"msg": "Usuario y contraseña son obligatorios"}), 400

    usuario = Usuario.query.filter_by(username=username).first()

    if not usuario or not usuario.check_password(password):
        return jsonify({"msg": "Credenciales inválidas"}), 401

    # Crear token con duración de 1 hora
    access_token = create_access_token(
        identity=usuario.id,
        expires_delta=datetime.timedelta(hours=1)
    )

    return jsonify(access_token=access_token), 200
