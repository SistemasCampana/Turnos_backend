# flaskr/__init__.py
from flask_migrate import Migrate
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import cloudinary
import os
from flask_cors import CORS  

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name='default'):
    app = Flask(__name__)

    cloudinary.config(
        cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME', 'dz6c95uv6'),
        api_key=os.environ.get('CLOUDINARY_API_KEY', '827636139563183'),
        api_secret=os.environ.get('CLOUDINARY_API_SECRET', 'pR_UNAWeUsijnZnS_7weISDue0Y')
    )

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'dev-secret-change-me')

    # 🔹 Configurar conexión a DB
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
    else:
        db_user = os.environ.get("DB_USER", "root")
        db_password = os.environ.get("DB_PASSWORD", "")
        db_host = os.environ.get("DB_HOST", "localhost")
        db_port = os.environ.get("DB_PORT", "3306")
        db_name = os.environ.get("DB_NAME", "turnero")
        database_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['FLASK_RUN_PORT'] = int(os.environ.get("PORT", 5001))

    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=False)

    db.init_app(app)
    migrate.init_app(app, db, directory="migrations")

    # 🔹 Importar modelos y controladores
    from flaskr import modelos
    from flaskr.modelos import Usuario, Turno
    from flaskr.controllers.turno_controller import turno_bp
    from flaskr.controllers.login_controller import login_bp
    app.register_blueprint(turno_bp, url_prefix="/api/turnos")
    app.register_blueprint(login_bp, url_prefix="/api")

    # 🔹 Solo en producción: manejar creación de tablas una por una
    if os.environ.get('FLASK_ENV') == 'production':
        with app.app_context():
            from sqlalchemy import inspect
            insp = inspect(db.engine)
            tablas = insp.get_table_names()

            # Crear tabla usuarios si no existe
            if "usuarios" not in tablas:
                try:
                    Usuario.__table__.create(db.engine)
                    print("✅ Tabla 'usuarios' creada correctamente.")
                except Exception as e:
                    print("⚠️ Error creando la tabla 'usuarios':", e)
            else:
                print("ℹ️ La tabla 'usuarios' ya existe.")

            # Crear tabla turnos si no existe
            if "turnos" not in tablas:
                try:
                    Turno.__table__.create(db.engine)
                    print("✅ Tabla 'turnos' creada correctamente.")
                except Exception as e:
                    print("⚠️ Error creando la tabla 'turnos':", e)
            else:
                print("ℹ️ La tabla 'turnos' ya existe.")

            # 🔹 Crear usuario administrador inicial
            if "usuarios" in insp.get_table_names():
                from werkzeug.security import generate_password_hash

                if Usuario.query.count() == 0:
                    username = "Administrador"
                    password = "Campana17"
                    hashed_password = generate_password_hash(password)
                    nuevo_usuario = Usuario(username=username, password_hash=hashed_password)
                    db.session.add(nuevo_usuario)
                    db.session.commit()
                    print(f"✅ Usuario '{username}' creado automáticamente.")
            else:
                print("⚠️ La tabla 'usuarios' aún no existe, no se creó el admin.")

    return app