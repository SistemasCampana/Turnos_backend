# flaskr/app.py
from flaskr import create_app
from flask_cors import CORS

# Crear la app con la configuración por defecto
app = create_app('default')

# Habilitar CORS
CORS(app)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
