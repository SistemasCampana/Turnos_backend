# flaskr/__init__.py
from flask_migrate import Migrate
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import cloudinary
import os

# Instancias globales
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name='default'):
    app = Flask(__name__)

    # 📦 Configuración de Cloudinary
    cloudinary.config(
        cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME', 'dz6c95uv6'),
        api_key=os.environ.get('CLOUDINARY_API_KEY', '827636139563183'),
        api_secret=os.environ.get('CLOUDINARY_API_SECRET', 'pR_UNAWeUsijnZnS_7weISDue0Y')
    )

    # 🔑 Llaves secretas (JWT y Flask)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'dev-secret-change-me')

    # 🔄 Base de datos: usar DATABASE_URL si existe (Render/PostgreSQL), sino usar MySQL local
    database_url = os.environ.get("DATABASE_URL")

    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
    else:
        # Construir conexión MySQL local
        db_user = os.environ.get("DB_USER", "root")
        db_password = os.environ.get("DB_PASSWORD", "")
        db_host = os.environ.get("DB_HOST", "localhost")
        db_port = os.environ.get("DB_PORT", "3306")
        db_name = os.environ.get("DB_NAME", "turnero")
        database_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['FLASK_RUN_PORT'] = int(os.environ.get("PORT", 5001))

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db, directory="migrations")

    # Registrar modelos
    from flaskr import modelos

    # Registrar blueprints
    from flaskr.controllers.turno_controller import turno_bp
    from flaskr.controllers.login_controller import login_bp
    app.register_blueprint(turno_bp, url_prefix="/api/turnos")
    app.register_blueprint(login_bp, url_prefix="/api")

    # 🚀 Migraciones automáticas en producción (Render)
    if os.environ.get('FLASK_ENV') == 'production':
        with app.app_context():
            from flask_migrate import upgrade
            upgrade()
            
            # Crear usuario inicial automáticamente si no hay usuarios
            from flaskr.modelos import Usuario
            from werkzeug.security import generate_password_hash

            if Usuario.query.count() == 0:
                username = "Administrador"
                password = "Campana17"
                hashed_password = generate_password_hash(password)
                nuevo_usuario = Usuario(username=username, password_hash=hashed_password)
                db.session.add(nuevo_usuario)
                db.session.commit()
                print(f"✅ Usuario '{username}' creado automáticamente.")

    return app
