from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import cloudinary
import cloudinary.uploader
import cloudinary.api
import os  # 👈 Para leer variables de entorno

def create_app(config_name):
    app = Flask(__name__)
    
    # 🔑 Configuración de Cloudinary
    cloudinary.config(
        cloud_name='dz6c95uv6',
        api_key='827636139563183',
        api_secret='pR_UNAWeUsijnZnS_7weISDue0Y'
    )
    
    # 🔑 Llaves secretas
    app.config['SECRET_KEY'] = 'Jaider1206'
    app.config['JWT_SECRET_KEY'] = 'Jaider1206'
    
    # 🔄 Usar la base de datos de Render (PostgreSQL)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
    
    # ⚡ Configuración adicional
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['FLASK_RUN_PORT'] = 5001
    
    return app
