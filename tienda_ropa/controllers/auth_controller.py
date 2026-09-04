from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_user, logout_user, current_user
from models.user import User
from database import db

auth_bp = Blueprint('auth', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/auth', methods=['GET', 'POST'])
def auth():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('dashboard.admin_dashboard'))
        return redirect(url_for('dashboard.index'))

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
                return redirect(url_for('auth.auth', tab='login'))

            if user.role != selected_role:
                flash(f'La cuenta no tiene permisos de {selected_role}. Verifica tu selección de rol.', 'warning')
                return redirect(url_for('auth.auth', tab='login'))

            login_user(user, remember=remember)
            next_page = request.args.get('next')
            flash(f'¡Bienvenido de nuevo, {user.name}!', 'success')
            
            if user.role == 'admin':
                return redirect(next_page or url_for('dashboard.admin_dashboard'))
            return redirect(next_page or url_for('dashboard.index'))

        elif form_type == 'register':
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')

            if not name or not email or not password:
                flash('Todos los campos son obligatorios.', 'error')
                return redirect(url_for('auth.auth', tab='register'))

            if not email.endswith('@gmail.com'):
                flash('Debes utilizar un correo de @gmail.com para registrarte.', 'error')
                return redirect(url_for('auth.auth', tab='register'))

            if len(password) < 6:
                flash('La contraseña debe tener al menos 6 caracteres.', 'error')
                return redirect(url_for('auth.auth', tab='register'))

            if User.query.filter_by(email=email).first():
                flash('Este correo ya está registrado. Intenta iniciar sesión.', 'error')
                return redirect(url_for('auth.auth', tab='register'))

            new_user = User(name=name, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user)
            flash(f'¡Cuenta creada con éxito! Bienvenido, {new_user.name}.', 'success')
            return redirect(url_for('dashboard.index'))

    return render_template('auth.html', active_tab=active_tab)

@auth_bp.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash('Has cerrado sesión correctamente.', 'success')
    return redirect(url_for('auth.auth'))
