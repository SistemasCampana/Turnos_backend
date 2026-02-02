from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flaskr.modelos.modelos import db, Usuario 
from flaskr.controllers.login_controller import login_bp
from flaskr.controllers.turno_controller import turno_bp 
from werkzeug.security import generate_password_hash
import os

def create_app():
    app = Flask(__name__)

    # 1. CONFIGURACIÓN DE BASE DE DATOS
    database_url = os.getenv('DATABASE_URL')
    
    # IMPORTANTE: Render a veces entrega la URL con "postgres://", 
    # SQLAlchemy requiere "postgresql://" para funcionar correctamente.
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "connect_args": {
            "options": "-c client_encoding=utf8"
        }
    }

    # 2. CONFIGURACIÓN DE CORS (SOLUCIÓN DEFINITIVA)
    # Cambiamos "origins" a "*" temporalmente para asegurar la conexión en producción,
    # esto evita el error de "preflight request" que bloqueaba a maria torres.
    CORS(app, resources={r"/api/*": {
        "origins": "*", 
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }})

    # 3. JWT CONFIG
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-campana')
    jwt = JWTManager(app)

    # 4. INICIALIZACIÓN DE DB Y MIGRACIONES
    db.init_app(app)
    migrate = Migrate(app, db)

    # 5. REGISTRO DE RUTAS
    # Asegúrate de que en turno_controller.py el blueprint se llame exactamente 'turno_bp'
    app.register_blueprint(login_bp, url_prefix='/api')
    app.register_blueprint(turno_bp, url_prefix='/api') 

    # 6. CREACIÓN AUTOMÁTICA DE TABLAS Y ADMIN
    with app.app_context():
        try:
            db.create_all() 
            if not Usuario.query.filter_by(username="Administrador").first():
                admin = Usuario(
                    username="Administrador",
                    password_hash=generate_password_hash("Campana17"),
                    sede="Paloquemao",
                    rol="administrador"
                )
                db.session.add(admin)
                db.session.commit()
                print("✅ Base de datos lista y Administrador creado.")
        except Exception as e:
            print(f"❌ Error al inicializar la base de datos: {e}")

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    # Importante: host='0.0.0.0' es obligatorio para que Render sea visible
    app.run(debug=False, host='0.0.0.0', port=port)