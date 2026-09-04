import os

from flask import Flask

try:
    from .database import db
    from .models.cliente import Cliente
    from .models.venta import Venta
    from .controllers.dashboard_controller import dashboard_bp
except ImportError:
    from database import db
    from models.cliente import Cliente
    from models.venta import Venta
    from controllers.dashboard_controller import dashboard_bp


def create_app():
    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='static'
    )

    base_dir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(base_dir, 'instance', 'tienda_ropa.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    app.register_blueprint(dashboard_bp)

    with app.app_context():
        db.create_all()
        if Cliente.query.first() is None:
            seed_data()

    return app


def seed_data():
    clientes = [
        Cliente(nombre='Camila Torres', categoria_favorita='Vestidos', segmento='VIP'),
        Cliente(nombre='Mateo Gómez', categoria_favorita='Camisetas/Tops', segmento='Frecuente'),
        Cliente(nombre='Sofía Morales', categoria_favorita='Pantalones/Jeans', segmento='Nuevo'),
        Cliente(nombre='Lucía Fernández', categoria_favorita='Calzado', segmento='Frecuente'),
    ]
    db.session.add_all(clientes)
    db.session.commit()

    ventas = [
        Venta(monto=150.0, categoria_producto='Vestidos', cliente_id=clientes[0].id),
        Venta(monto=85.5, categoria_producto='Camisetas/Tops', cliente_id=clientes[1].id),
        Venta(monto=95.0, categoria_producto='Pantalones/Jeans', cliente_id=clientes[2].id),
        Venta(monto=120.0, categoria_producto='Calzado', cliente_id=clientes[3].id),
    ]
    db.session.add_all(ventas)
    db.session.commit()
    print('Base de datos inicializada con datos de prueba.')


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)