import os
from functools import wraps
from flask import Flask, render_template, redirect, url_for, request, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'clave-super-secreta-cambia-en-produccion')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tienda.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
login_manager.login_message_category = 'warning'

class User(UserMixin, db.Model):

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

    role = db.Column(db.String(20), default='client')

    def set_password(self, plain_password):

        self.password = generate_password_hash(plain_password)

    def check_password(self, plain_password):

        return check_password_hash(self.password, plain_password)

@login_manager.user_loader
def load_user(user_id):

    return db.session.get(User, int(user_id))

def admin_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():

    return render_template('index.html')

@app.route('/auth', methods=['GET', 'POST'])
def auth():

    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('index'))

    active_tab = request.args.get('tab', 'login')

    if request.method == 'POST':
        form_type = request.form.get('form_type')

        if form_type == 'login':
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            selected_role = request.form.get('role', 'client')
            remember = True if request.form.get('remember') else False

            user = User.query.filter_by(email=email).first()

            if not user or not user.check_password(password):
                flash('Correo o contraseña incorrectos. Inténtalo de nuevo.', 'error')
                return redirect(url_for('auth', tab='login'))

            if user.role != selected_role:
                flash(f'La cuenta no tiene permisos de {selected_role}. Verifica tu selección de rol.', 'warning')
                return redirect(url_for('auth', tab='login'))

            login_user(user, remember=remember)
            next_page = request.args.get('next')
            flash(f'¡Bienvenido de nuevo, {user.name}!', 'success')

            if user.role == 'admin':
                return redirect(next_page or url_for('admin_dashboard'))
            return redirect(next_page or url_for('index'))

        elif form_type == 'register':
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')

            if not name or not email or not password:
                flash('Todos los campos son obligatorios.', 'error')
                return redirect(url_for('auth', tab='register'))

            if not email.endswith('@gmail.com'):
                flash('Debes utilizar un correo de @gmail.com para registrarte.', 'error')
                return redirect(url_for('auth', tab='register'))

            if len(password) < 6:
                flash('La contraseña debe tener al menos 6 caracteres.', 'error')
                return redirect(url_for('auth', tab='register'))

            if User.query.filter_by(email=email).first():
                flash('Este correo ya está registrado. Intenta iniciar sesión.', 'error')
                return redirect(url_for('auth', tab='register'))

            new_user = User(name=name, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user)
            flash(f'¡Cuenta creada con éxito! Bienvenido, {new_user.name}.', 'success')
            return redirect(url_for('index'))

    return render_template('auth.html', active_tab=active_tab)

@app.route('/logout')
@login_required
def logout():

    logout_user()
    flash('Has cerrado sesión correctamente.', 'success')
    return redirect(url_for('auth'))

@app.route('/admin')
@admin_required
def admin_dashboard():

    return render_template('admin_dashboard.html')

@app.route('/crear_admin_test')
def crear_admin_test():

    if User.query.filter_by(email='admin@tienda.com').first():
        return "El admin ya existe. Haz login con admin@tienda.com"

    admin = User(name='Admin Principal', email='admin@tienda.com', role='admin')
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    return "Admin creado exitosamente con el correo admin@tienda.com y contraseña admin123"

if __name__ == '__main__':

    with app.app_context():
        db.create_all()

    app.run(debug=True)
