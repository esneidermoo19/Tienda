from flask import Blueprint, render_template
from sqlalchemy import func

try:
    from ..models.cliente import Cliente
    from ..models.venta import Venta
    from ..database import db
except ImportError:
    from models.cliente import Cliente
    from models.venta import Venta
    from database import db

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def index():
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

    data = {
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

    return data


@dashboard_bp.route('/')
def index():
    return render_template('dasbo_admin.html', data=_get_dashboard_data())


@dashboard_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', data=_get_dashboard_data())
