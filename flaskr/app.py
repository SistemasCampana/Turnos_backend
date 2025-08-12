# flaskr/app.py
import os
from flaskr import create_app, db
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate

app = create_app('default')

# Habilitar CORS
CORS(app, supports_credentials=True)

# JWT
app.config['JWT_SECRET_KEY'] = os.environ.get(
    'JWT_SECRET_KEY',
    app.config.get('JWT_SECRET_KEY', 'dev-secret-change-me')
)
jwt = JWTManager(app)

# Migraciones
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
