from flask import Flask, jsonify, request
from models import db
from products_service import products_bp
from customers_service import customers_bp
from orders_service import orders_bp

app = Flask(__name__)

app.config.from_object('db_config')

db.init_app(app)

# Register all blueprints
app.register_blueprint(products_bp)
app.register_blueprint(customers_bp)
app.register_blueprint(orders_bp)

@app.route('/')  # Root path
def home():
    return jsonify({
        'message': 'Welcome to the RESTful API',
        'endpoints': {
            'customers': '/api/customers',
            'orders': '/api/orders',
            'products': '/api/products'
        }
    })

if __name__ == '__main__':
    app.run(debug=True)

