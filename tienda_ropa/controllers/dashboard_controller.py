from flask import Blueprint, render_template
from sqlalchemy import func

try:
    from ..database import db
    from ..models.cliente import Cliente
    from ..models.venta import Venta
except ImportError:
    from database import db
    from models.cliente import Cliente
    from models.venta import Venta

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

    return render_template('dashboard.html', data=data)


@dashboard_bp.route('/admin')
@dashboard_bp.route('/dasbo_admin')
def admin_dashboard():
    total_clientes = Cliente.query.count()
    clientes_vip = Cliente.query.filter_by(segmento='VIP').count()
    promedio_venta = db.session.query(func.avg(Venta.monto)).scalar() or 0.0
    ventas_totales = db.session.query(func.sum(Venta.monto)).scalar() or 0.0
    pedidos_completados = db.session.query(func.count(Venta.id)).scalar() or 0

    data = {
        'metricas': {
            'ingresos_totales': ventas_totales,
            'pedidos_completados': pedidos_completados,
            'ticket_promedio': promedio_venta,
            'tasa_conversion': 2.8,
            'clientes_vip': clientes_vip,
            'total_clientes': total_clientes,
        },
        'top_productos': [
            {'producto': 'Vestido Floral de Verano', 'categoria': 'Mujer', 'unidades': 85, 'ingresos': 2550, 'stock': 12},
            {'producto': 'Tenis Blancos Clásicos', 'categoria': 'Calzado', 'unidades': 60, 'ingresos': 3600, 'stock': 25},
            {'producto': 'Camiseta Básica (Pack 3)', 'categoria': 'Hombre', 'unidades': 55, 'ingresos': 1100, 'stock': 40},
            {'producto': 'Chaqueta Denim Oversize', 'categoria': 'Mujer', 'unidades': 42, 'ingresos': 1890, 'stock': 4},
            {'producto': 'Bolso Bandolera Cuero', 'categoria': 'Accesorios', 'unidades': 30, 'ingresos': 1500, 'stock': 18},
        ],
        'alertas': [
            'Stock Crítico: La "Chaqueta Denim Oversize" y el "Pantalón Cargo Beige (M)" tienen menos de 5 unidades. Reponer antes del fin de semana.',
            'Carritos Abandonados: 45 usuarios dejaron artículos en las últimas 24 horas. Oportunidad para email con 10% de descuento.',
            'Devoluciones: 12 artículos devueltos esta semana. Principal motivo: "Talla incorrecta" en calzado. Actualizar guía de tallas.'
        ]
    }

    return render_template('dasbo_admin.html', data=data)