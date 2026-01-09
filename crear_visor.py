from flaskr.app import app
from flaskr.modelos.modelos import db, Usuario
from werkzeug.security import generate_password_hash


with app.app_context():
    # 1. Encriptar la clave
    hash_clave = generate_password_hash("Usuarioprueba")
    
    # 2. Crear el objeto
    nuevo_visor = Usuario(
        username="usuarioprueba",
        password_hash=hash_clave,
        rol="visor"
    )
    # 3. Guardar en la base de datos
    db.session.add(nuevo_visor)
    db.session.commit()
    print("Usuario visor creado con éxito.")