"""
FinAI - Production WSGI Application Entry Point
Supports deployment on production WSGI servers:
  - Windows / Cross-platform: Waitress (waitress-serve --host=127.0.0.1 --port=5000 wsgi:app)
  - Linux / UNIX: Gunicorn (gunicorn -w 4 -b 127.0.0.1:5000 wsgi:app)
"""

import os
import sys

# Enforce secure production defaults before loading app
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('FLASK_DEBUG', 'False')

from config import Config
from app import create_app

# WSGI application callable for servers
app = create_app(Config)

if __name__ == '__main__':
    host = Config.FLASK_HOST
    port = Config.PORT
    try:
        import waitress
        print(f"[WSGI] Serving FinAI with Waitress production server on http://{host}:{port}")
        waitress.serve(app, host=host, port=port)
    except ImportError:
        print("[WSGI] 'waitress' not found. For production deployments, install waitress (pip install waitress).")
        print(f"[WSGI] Falling back to standard server on http://{host}:{port} with debug=False")
        app.run(host=host, port=port, debug=False)
