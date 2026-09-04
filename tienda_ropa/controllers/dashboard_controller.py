from flask import Blueprint, render_template, redirect, url_for, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func

try:
    from models.cliente import Cliente
    from models.venta import Venta
    from database import db
    from controllers.auth_controller import admin_required
except ImportError:
    from tienda_ropa.models.cliente import Cliente
    from tienda_ropa.models.venta import Venta
    from tienda_ropa.database import db
    from tienda_ropa.controllers.auth_controller import admin_required

dashboard_bp = Blueprint('dashboard', __name__)


def _get_dashboard_data():
    total_clientes = Cliente.query.count()
    clientes_vip = Cliente.query.filter_by(segmento='VIP').count()
    promedio_venta = db.session.query(func.avg(Venta.monto)).scalar() or 0.0
    clientes = Cliente.query.order_by(Cliente.id.desc()).limit(10).all()

    categorias_query = db.session.query(
        Venta.categoria_producto,
        func.count(Venta.id)
    ).group_by(Venta.categoria_producto).all()

    categorias_labels = [categoria for categoria, _ in categorias_query] or ['Camisetas', 'Jeans', 'Vestidos', 'Calzado']
    categorias_valores = [count for _, count in categorias_query] or [35, 25, 20, 20]
    total_ventas = sum(categorias_valores)

    if total_ventas:
        porcentajes = [round((count / total_ventas) * 100, 1) for count in categorias_valores]
    else:
        porcentajes = [35, 25, 20, 20]

    return {
        'metricas': {
            'total_clientes': total_clientes,
            'clientes_frecuentes': clientes_vip,
            'ticket_promedio': round(promedio_venta, 2),
            'tasa_devolucion': 3.2
        },
        'grafico_ventas_mensuales': {
            'meses': ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'],
            'ventas_dolares': [12400, 15800, 14200, 18900, 21000, 24500]
        },
        'grafico_categorias': {
            'categorias': categorias_labels,
            'porcentajes': porcentajes
        },
        'ultimos_clientes': [cliente.to_dict() for cliente in clientes]
    }


def _get_admin_dashboard_data():
    total_clientes = Cliente.query.count()
    clientes_vip = Cliente.query.filter_by(segmento='VIP').count()
    promedio_venta = db.session.query(func.avg(Venta.monto)).scalar() or 0.0
    ventas_totales = db.session.query(func.sum(Venta.monto)).scalar() or 0.0
    pedidos_completados = db.session.query(func.count(Venta.id)).scalar() or 0

    top_productos = [
        {'producto': 'Vestido Midi Floral', 'categoria': 'Vestidos', 'unidades': 142, 'ingresos': 7100.0, 'stock': 18},
        {'producto': 'Camiseta Básica Algodón', 'categoria': 'Camisetas/Tops', 'unidades': 120, 'ingresos': 3600.0, 'stock': 4},
        {'producto': 'Jeans Slim Fit', 'categoria': 'Pantalones/Jeans', 'unidades': 95, 'ingresos': 4750.0, 'stock': 12},
        {'producto': 'Zapatillas Urban Leather', 'categoria': 'Calzado', 'unidades': 68, 'ingresos': 5440.0, 'stock': 3},
        {'producto': 'Chaqueta Denim Oversize', 'categoria': 'Abrigos', 'unidades': 45, 'ingresos': 3600.0, 'stock': 15},
    ]

    alertas = [
        {
            'tipo': 'danger',
            'icono': '⚠️',
            'titulo': 'Stock Crítico',
            'mensaje': '2 productos cuentan con 5 o menos unidades disponibles en inventario.'
        },
        {
            'tipo': 'warning',
            'icono': '🛒',
            'titulo': 'Carritos Abandonados',
            'mensaje': '14 carritos en las últimas 24 horas con valor potencial de $1,280.'
        },
        {
            'tipo': 'info',
            'icono': '🔄',
            'titulo': 'Devoluciones',
            'mensaje': '3 solicitudes pendientes de revisión por garantía.'
        }
    ]

    departamentos = [
        {'nombre': 'Ropa de Mujer', 'monto': 7500, 'porcentaje': 48, 'color_class': 'primary'},
        {'nombre': 'Ropa de Hombre', 'monto': 4500, 'porcentaje': 29, 'color_class': 'success'},
        {'nombre': 'Accesorios y Calzado', 'monto': 3400, 'porcentaje': 23, 'color_class': 'warning'},
    ]

    return {
        'kpis': {
            'ingresos_totales': ventas_totales if ventas_totales > 0 else 15400.0,
            'pedidos_completados': pedidos_completados if pedidos_completados > 0 else 342,
            'ticket_promedio': round(promedio_venta, 2) if promedio_venta > 0 else 45.03,
            'tasa_conversion': 2.8,
            'total_clientes': total_clientes,
            'clientes_vip': clientes_vip,
        },
        'top_productos': top_productos,
        'alertas': alertas,
        'departamentos': departamentos,
    }


@dashboard_bp.route('/')
@login_required
def index():
    if current_user.is_authenticated and current_user.role == 'admin':
        return redirect(url_for('dashboard.admin_dashboard'))
    return render_template('dashboard.html', data=_get_dashboard_data())


@dashboard_bp.route('/api/dashboard')
@login_required
def api_dashboard():
    return jsonify(_get_dashboard_data())


@dashboard_bp.route('/admin')
@dashboard_bp.route('/dasbo_admin')
@admin_required
def admin_dashboard():
    data = _get_admin_dashboard_data()
    return render_template('dasbo_admin.html', data=data)


@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', data=_get_dashboard_data())

