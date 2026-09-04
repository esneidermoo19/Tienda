import os
import sys

# Asegurar que el paquete tienda_ropa esté en el path de módulos
base_dir = os.path.abspath(os.path.dirname(__file__))
tienda_dir = os.path.join(base_dir, 'tienda_ropa')
if tienda_dir not in sys.path:
    sys.path.insert(0, tienda_dir)

from tienda_ropa.app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

