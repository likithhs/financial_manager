"""
Finora - Production WSGI Application Entry Point
Supports deployment on production WSGI servers:
  - Linux / Cloud PaaS (Docker, Render, Heroku, Railway, AWS): Gunicorn
  - Windows / Cross-platform: Waitress
"""

import os
import sys

# Enforce secure production defaults before loading app
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('FLASK_DEBUG', 'False')

from config import Config
from app import create_app

# WSGI application callable for production servers
app = create_app(Config)
application = app  # Standard alias for WSGI servers (Gunicorn, uWSGI, AWS Elastic Beanstalk)

if __name__ == '__main__':
    host = os.environ.get('FLASK_HOST', Config.FLASK_HOST)
    port = int(os.environ.get('PORT', Config.PORT))
    
    # In cloud environments, bind to 0.0.0.0
    if os.environ.get('RENDER') or os.environ.get('PORT') or os.environ.get('DYNO'):
        host = '0.0.0.0'

    try:
        import waitress
        print(f"[WSGI] Serving Finora with Waitress production server on http://{host}:{port}")
        waitress.serve(app, host=host, port=port)
    except ImportError:
        print("[WSGI] Waitress not found. Serving with standard WSGI server...")
        app.run(host=host, port=port, debug=False)
