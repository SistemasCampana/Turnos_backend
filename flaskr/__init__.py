import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import cloudinary

# Inicialización de extensiones
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_name='default'):
    app = Flask(__name__)

    # 1. 🛡️ SEGURIDAD: Configuración de CORS para comunicación con React
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

    # 2. 🔑 CLAVES DE SEGURIDAD
    app.config['SECRET_KEY'] = 'dev-secret-campana'
    app.config['JWT_SECRET_KEY'] = 'dev-jwt-campana'

    # 3. 🐘 CONFIGURACIÓN POSTGRESQL (RENDER EXTERNAL - UTF8)
    # URL actualizada a turnos_campana
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://turnos_campana:8hRelnibw0oFDunYyAwVp20RrIHxoSSA@dpg-d5ufmdu3jp1c739v8e7g-a.oregon-postgres.render.com/turnos_campana'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 🛠️ SOLUCIÓN AL ERROR DE ENCODING: Forzamos UTF8 en la comunicación con Render
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "connect_args": {
            "options": "-c client_encoding=utf8"
        }
    }

    # 4. ☁️ CLOUDINARY
    cloudinary.config(
        cloud_name='dz6c95uv6',
        api_key='827636139563183',
        api_secret='pR_UNAWeUsijnZnS_7weISDue0Y'
    )

    # Inicializar las extensiones con la app
    db.init_app(app)
    migrate.init_app(app, db, directory="migrations")
    jwt.init_app(app)

    # 5. CONTROLADORES (Blueprints)
    from flaskr.controllers.turno_controller import turno_bp
    from flaskr.controllers.login_controller import login_bp
    
    # Registro de rutas (Asegúrate de que los nombres de los BP coincidan)
    app.register_blueprint(turno_bp, url_prefix="/api")
    app.register_blueprint(login_bp, url_prefix="/api")

    # 6. 🚀 INICIALIZACIÓN DE BASE DE DATOS Y ADMIN
    with app.app_context():
        try:
            from flaskr.modelos.modelos import Usuario 
            db.create_all() # Esto creará todas las tablas en la base de datos vacía
            
            # Crear usuario administrador por defecto si no existe
            if not Usuario.query.filter_by(username="Administrador").first():
                from werkzeug.security import generate_password_hash
                admin = Usuario(
                    username="Administrador",
                    password_hash=generate_password_hash("Campana17"),
                    sede="Paloquemao",
                    rol="administrador"
                )
                db.session.add(admin)
                db.session.commit()
                print("✅ Tablas creadas y Usuario Administrador verificado en Render (UTF8)")
        except Exception as e:
            # Ahora este print nos dirá el error exacto si falla la conexión
            print(f"❌ Error de conexión en PostgreSQL: {e}")

    return app