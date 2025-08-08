from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
import cloudinary
import cloudinary.uploader
import cloudinary.api
import os

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Configuración de Cloudinary
    cloudinary.config(
        cloud_name='dz6c95uv6',
        api_key='827636139563183',
        api_secret='pR_UNAWeUsijnZnS_7weISDue0Y'
    )
    
    # Llaves secretas para sesiones y JWT
    app.config['SECRET_KEY'] = 'Jaider1206'
    app.config['JWT_SECRET_KEY'] = 'Jaider1206'
    
    # Base de datos (Render usa DATABASE_URL)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['FLASK_RUN_PORT'] = 5001

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Registrar blueprints
    from flaskr.turnos import turno_bp
    app.register_blueprint(turno_bp, url_prefix="/api/turnos")

    # ✅ Evitar que JWT bloquee rutas públicas
    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        from flask import request, jsonify
        if request.path.startswith("/api/turnos"):
            # Permitimos acceso sin token
            return jsonify({"msg": "Ruta pública, no requiere token"}), 200
        return jsonify({"msg": "Falta token o es inválido"}), 401

    return app
