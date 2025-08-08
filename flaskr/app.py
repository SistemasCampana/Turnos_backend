# flaskr/app.py
from flaskr import create_app
from flaskr.modelos import db
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flaskr.controllers.turno_controller import turno_bp
from flask_cors import CORS

app = create_app('default')
CORS(app)


db.init_app(app)
JWTManager(app)
Migrate(app, db)


app.register_blueprint(turno_bp, url_prefix="/api/turnos")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
