from flask import Blueprint, render_template
from models.cliente import Cliente
from models.venta import Venta
from database import db
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    # 1. Consultas y métricas principales
    total_clientes = Cliente.query.count()
    clientes_vip = Cliente.query.filter_by(segmento='VIP').count()
    
    # Promedio de ventas (Ticket promedio)
    promedio_venta = db.session.query(func.avg(Venta.monto)).scalar() or 0.0
    
    # Obtener últimos clientes registrados/activos
    clientes = Cliente.query.order_by(Cliente.id.desc()).limit(10).all()

    # 2. Datos para gráficos
    # Porcentaje de ventas por categoría
    categorias_query = db.session.query(
        Venta.categoria_producto, 
        func.count(Venta.id)
    ).group_by(Venta.categoria_producto).all()

    categorias_labels = [c[0] for c in categorias_query] if categorias_query else ["Camisetas", "Jeans", "Vestidos", "Calzado"]
    categorias_valores = [c[1] for c in categorias_query] if categorias_query else [35, 25, 20, 20]

    data = {
        "metricas": {
            "total_clientes": total_clientes,
            "clientes_frecuentes": clientes_vip,
            "ticket_promedio": round(promedio_venta, 2),
            "tasa_devolucion": 3.2  # Métrica simulada
        },
        "grafico_ventas_mensuales": {
            "meses": ["Ene", "Feb", "Mar", "Abr", "May", "Jun"],
            "ventas_dolares": [12400, 15800, 14200, 18900, 21000, 24500]
        },
        "grafico_categorias": {
            "categorias": categorias_labels,
            "porcentajes": categorias_valores
        },
        "ultimos_clientes": [c.to_dict() for c in clientes]
    }

    return render_template('dashboard.html', data=data)