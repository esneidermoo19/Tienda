import os
from flask import Flask
from flask_login import LoginManager

try:
    from database import db
    from models.cliente import Cliente
    from models.venta import Venta
    from models.user import User
    from controllers.dashboard_controller import dashboard_bp
    from controllers.auth_controller import auth_bp
except ImportError:
    from tienda_ropa.database import db
    from tienda_ropa.models.cliente import Cliente
    from tienda_ropa.models.venta import Venta
    from tienda_ropa.models.user import User
    from tienda_ropa.controllers.dashboard_controller import dashboard_bp
    from tienda_ropa.controllers.auth_controller import auth_bp

def create_app():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(base_dir)
    instance_dir = os.path.join(root_dir, 'instance')
    os.makedirs(instance_dir, exist_ok=True)
    db_path = os.path.join(instance_dir, 'tienda_ropa.db').replace('\\', '/')

    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, 'templates'),
        static_folder=os.path.join(base_dir, 'static')
    )
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'clave-super-secreta')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializar extensiones
    db.init_app(app)

    # Configuración de Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.auth'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Registrar blueprints
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(auth_bp)

    # Crear tablas y sembrar datos de prueba si la BD está vacía
    with app.app_context():
        db.create_all()
        seed_data()

    return app

def seed_data():
    admin = User.query.filter_by(email="admin@tienda.com").first()
    if not admin:
        admin = User(name="Admin Principal", email="admin@tienda.com", role="admin")
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print("Admin de prueba creado (admin@tienda.com / admin123).")
    elif admin.role != 'admin':
        admin.role = 'admin'
        db.session.commit()

    cliente_demo = User.query.filter_by(email="cliente@tienda.com").first()
    if not cliente_demo:
        cliente_demo = User(name="Cliente Demo", email="cliente@tienda.com", role="client")
        cliente_demo.set_password("cliente123")
        db.session.add(cliente_demo)
        db.session.commit()
        print("Cliente demo creado (cliente@tienda.com / cliente123).")

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
        print("Base de datos inicializada con datos de prueba.")

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)