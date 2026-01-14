from flask_migrate import Migrate
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
import cloudinary
import os
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name='default'):
    app = Flask(__name__)

    # 🔹 CONFIGURACIÓN DE CORS (CORREGIDA PARA ELIMINAR EL ERROR DE CONEXIÓN)
    # Cambiamos /api/* por /* y permitimos todos los métodos y cabeceras
    CORS(app, resources={r"/*": {
    "origins": "*",
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Origin"],
    "expose_headers": ["Content-Type", "Authorization"]
}}, supports_credentials=True)

    cloudinary.config(
        cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME', 'dz6c95uv6'),
        api_key=os.environ.get('CLOUDINARY_API_KEY', '827636139563183'),
        api_secret=os.environ.get('CLOUDINARY_API_SECRET', 'pR_UNAWeUsijnZnS_7weISDue0Y')
    )

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'dev-secret-change-me')

    # 🔹 Configurar conexión a DB
    database_url = os.environ.get("DATABASE_URL")
    
    is_postgres = False
    
    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        
        if database_url.startswith("postgresql://"):
             is_postgres = True
             
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
    
    if is_postgres:
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'connect_args': {
                'sslmode': 'require' 
            }
        }

    db.init_app(app)
    migrate.init_app(app, db, directory="migrations")

    # 🔹 Importar modelos y controladores
    from flaskr import modelos
    from flaskr.modelos import Usuario, Turno
    from flaskr.controllers.turno_controller import turno_bp
    from flaskr.controllers.login_controller import login_bp
    
    # Asegúrate de que los prefijos coincidan con las llamadas del frontend
    app.register_blueprint(turno_bp, url_prefix="/api/turnos")
    app.register_blueprint(login_bp, url_prefix="/api")

    # 🔹 Solo en producción: manejar creación de tablas
    if os.environ.get('FLASK_ENV') == 'production':
        with app.app_context():
            try:
                insp = inspect(db.engine)
                tablas = insp.get_table_names()

                if "usuarios" not in tablas:
                    try:
                        Usuario.__table__.create(db.engine)
                        print("✅ Tabla 'usuarios' creada.")
                    except Exception as e:
                        print("⚠️ Error tabla usuarios:", e)

                if "turnos" not in tablas:
                    try:
                        Turno.__table__.create(db.engine)
                        print("✅ Tabla 'turnos' creada.")
                    except Exception as e:
                        print("⚠️ Error tabla turnos:", e)

                insp = inspect(db.engine)
                tablas_actualizadas = insp.get_table_names()

                if "usuarios" in tablas_actualizadas:
                    from werkzeug.security import generate_password_hash
                    if Usuario.query.count() == 0:
                        username = "Administrador"
                        password = "Campana17"
                        hashed_password = generate_password_hash(password)
                        # Agregamos sede y rol por defecto para evitar errores 500
                        nuevo_usuario = Usuario(
                            username=username, 
                            password_hash=hashed_password,
                            sede="Paloquemao",
                            rol="Administrador"
                        )
                        db.session.add(nuevo_usuario)
                        db.session.commit()
                        print(f"✅ Admin '{username}' creado.")
            except Exception as e:
                print(f"❌ Error DB inicio: {e}")

    @app.route("/api/turnos/ultimo", methods=["HEAD", "GET"])
    def uptime_check():
        return ("", 200)

    return app