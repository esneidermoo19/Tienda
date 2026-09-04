from datetime import datetime

try:
    from ..database import db
except ImportError:
    from database import db


class Venta(db.Model):
    __tablename__ = 'ventas'

    id = db.Column(db.Integer, primary_key=True)
    monto = db.Column(db.Float, nullable=False)
    categoria_producto = db.Column(db.String(50), nullable=False)  # 'Camisetas', 'Jeans', etc.
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)