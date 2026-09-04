from database import db

class Cliente(db.Model):
    __tablename__ = 'clientes'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    categoria_favorita = db.Column(db.String(50), nullable=False)
    segmento = db.Column(db.String(20), nullable=False)  # 'VIP', 'Frecuente', 'Nuevo'
    
    # Relación con las ventas del cliente
    ventas = db.relationship('Venta', backref='cliente', lazy=True)

    def to_dict(self):
        total_gastado = sum(v.monto for v in self.ventas)
        return {
            "id": self.id,
            "nombre": self.nombre,
            "categoria_fav": self.categoria_favorita,
            "segmento": self.segmento,
            "compras": len(self.ventas),
            "total_gastado": f"${total_gastado:,.2f}"
        }