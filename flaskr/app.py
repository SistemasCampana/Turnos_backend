from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flaskr.modelos.modelos import db, Usuario # Importamos Usuario para el admin inicial
from flaskr.controllers.login_controller import login_bp
from flaskr.controllers.turno_controller import turno_bp 
from werkzeug.security import generate_password_hash
import os

def create_app():
    app = Flask(__name__)

    # 1. CONFIGURACIÓN DE BASE DE DATOS (NUEVA BASE DE DATOS UTF8)
    # Usamos la URL de turnos_campana y el driver psycopg2 para evitar errores de encoding
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    # 'postgresql+psycopg2://turnos_campana:8hRelnibw0oFDunYyAwVp20RrIHxoSSA@dpg-d5ufmdu3jp1c739v8e7g-a.oregon-postgres.render.com/turnos_campana'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Blindaje de Encoding para prevenir el error 'utf-8 codec can't decode'
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "connect_args": {
            "options": "-c client_encoding=utf8"
        }
    }

    # 2. CONFIGURACIÓN DE CORS
    CORS(app, resources={r"/api/*": {
    "origins": "*",
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
}})

    # 3. JWT CONFIG
    app.config['JWT_SECRET_KEY'] = 'dev-secret-campana' # Consistente con tu proyecto
    jwt = JWTManager(app)

    # 4. INICIALIZACIÓN DE DB Y MIGRACIONES
    db.init_app(app)
    migrate = Migrate(app, db)

    # 5. REGISTRO DE RUTAS
    app.register_blueprint(login_bp, url_prefix='/api')
    app.register_blueprint(turno_bp, url_prefix='/api') 

    # 6. CREACIÓN AUTOMÁTICA DE TABLAS Y ADMIN
    with app.app_context():
        try:
            db.create_all() # Crea todas las tablas definidas en modelos.py
            
            # Verificamos si existe el Administrador
            if not Usuario.query.filter_by(username="Administrador").first():
                admin = Usuario(
                    username="Administrador",
                    password_hash=generate_password_hash("Campana17"),
                    sede="Paloquemao", # Sede por defecto
                    rol="administrador"
                )
                db.session.add(admin)
                db.session.commit()
                print("✅ Tablas creadas y Usuario Administrador inicializado.")
        except Exception as e:
            print(f"❌ Error al inicializar la base de datos: {e}")

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)