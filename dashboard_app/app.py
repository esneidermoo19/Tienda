from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Datos simulados para tienda de ropa
ROPA_DASHBOARD_DATA = {
    "metricas": {
        "total_clientes": 1850,
        "clientes_frecuentes": 420,  # Clientes VIP / Recurrentes
        "ticket_promedio": 78.50,    # Gasto medio por compra ($)
        "tasa_devolucion": 3.2       # Porcentaje de devoluciones
    },
    "grafico_ventas_mensuales": {
        "meses": ["Ene", "Feb", "Mar", "Abr", "May", "Jun"],
        "ventas_dolares": [12400, 15800, 14200, 18900, 21000, 24500]
    },
    "grafico_categorias": {
        "categorias": ["Camisetas/Tops", "Pantalones/Jeans", "Vestidos", "Calzado", "Accesorios"],
        "porcentajes": [35, 25, 20, 12, 8]
    },
    "ultimos_clientes": [
        {"id": 101, "nombre": "Camila Torres", "categoria_fav": "Vestidos", "segmento": "VIP", "compras": 12, "total_gastado": "$1,450"},
        {"id": 102, "nombre": "Mateo Gómez", "categoria_fav": "Camisetas/Tops", "segmento": "Frecuente", "compras": 5, "total_gastado": "$380"},
        {"id": 103, "nombre": "Sofía Morales", "categoria_fav": "Pantalones/Jeans", "segmento": "Nuevo", "compras": 1, "total_gastado": "$95"},
        {"id": 104, "nombre": "Lucía Fernández", "categoria_fav": "Calzado", "segmento": "Frecuente", "compras": 7, "total_gastado": "$620"},
    ]
}

@app.route('/')
def dashboard():
    return render_template('dashboard.html', data=ROPA_DASHBOARD_DATA)

if __name__ == '__main__':
    app.run(debug=True)