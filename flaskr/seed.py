# seed.py
from flaskr import create_app, db
from flaskr.modelos import Usuario  # ajusta si tu modelo tiene otro nombre/clase
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Datos del usuario inicial
    username = "Administrador"
    password = "Campana17"

    # Verificar si ya existe
    user = Usuario.query.filter_by(username=username).first()
    if not user:
        hashed_password = generate_password_hash(password)
        nuevo_usuario = Usuario(username=username, password_hash=hashed_password)
        db.session.add(nuevo_usuario)
        db.session.commit()
        print(f"✅ Usuario '{username}' creado con éxito.")
    else:
        print(f"⚠️ El usuario '{username}' ya existe.")
