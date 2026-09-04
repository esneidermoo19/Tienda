from flask import Flask
from database import db
from models.cliente import Cliente
from models.venta import Venta
from controllers.dashboard_controller import dashboard_bp

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tienda_ropa.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializar extensiones
    db.init_app(app)

    # Registrar blueprints
    app.register_blueprint(dashboard_bp)

    # Crear tablas y sembrar datos de prueba si la BD está vacía
    with app.app_context():
        db.create_all()
        seed_data()

    return app

def seed_data():
    if Cliente.query.first() is None:
        c1 = Cliente(nombre="Camila Torres", categoria_favorita="Vestidos", segmento="VIP")
        c2 = Cliente(nombre="Mateo Gómez", categoria_favorita="Camisetas/Tops", segmento="Frecuente")
        c3 = Cliente(nombre="Sofía Morales", categoria_favorita="Pantalones/Jeans", segmento="Nuevo")
        c4 = Cliente(nombre="Lucía Fernández", categoria_favorita="Calzado", segmento="Frecuente")

        db.session.add_all([c1, c2, c3, c4])
        db.session.commit()

        # Ventas de prueba asociados a clientes
        v1 = Venta(monto=150.0, categoria_producto="Vestidos", cliente_id=c1.id)
        v2 = Venta(monto=85.5, categoria_producto="Camisetas/Tops", cliente_id=c2.id)
        v3 = Venta(monto=95.0, categoria_producto="Pantalones/Jeans", cliente_id=c3.id)
        v4 = Venta(monto=120.0, categoria_producto="Calzado", cliente_id=c4.id)

        db.session.add_all([v1, v2, v3, v4])
        db.session.commit()
        print(" Base de datos inicializada con datos de prueba.")

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)