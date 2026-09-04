import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Inicialización de extensiones
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # Cargar configuración
    app.config.from_object('config.Config')
    
    # Inicializar extensiones con la app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Cargador de usuario para Flask-Login
    @login_manager.user_loader
    def load_user(idusuario):
        from .models.usuario import User
        return User.query.get(int(idusuario))

    # Importar e inicializar los Controladores/Blueprints
    from .controllers.dashboard_controller import dashboard_bp
    app.register_blueprint(dashboard_bp)

    from .routes import (
        auth,user.py_route, servicios_route, perfil_route,
        galeria_route, catalogo_route, notificaciones_route
    )
    
    app.register_blueprint(auth.bp)
    
    app.register_blueprint(user.py.bp)
    app.register_blueprint(servicios_route.bp)
    app.register_blueprint(perfil_route.bp)
    app.register_blueprint(galeria_route.bp)
    app.register_blueprint(catalogo_route.bp)
    app.register_blueprint(notificaciones_route.bp)

    # Manejador global de errores
    @app.errorhandler(Exception)
    def handle_error(e):
        print(f"An error occurred: {str(e)}")
        return {"error": str(e)}, 500

    return app