from flask import Flask, jsonify, request
from models import db
from products_service import products_bp
from customers_service import customers_bp
from orders_service import orders_bp
from auth_service import auth_bp

app = Flask(__name__)

app.config.from_object('db_config')

db.init_app(app)

# Register all blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(products_bp)
app.register_blueprint(customers_bp)
app.register_blueprint(orders_bp)

@app.route('/')  # Root path
def home():
    return jsonify({
        'message': 'Welcome to the RBAC RESTful API',
        'endpoints': {
            'Authentication': {
                'login': {
                    'method': 'POST',
                    'path': '/api/login',
                    'description': 'Login to get JWT token',
                    'public': True
                },
                'register': {
                    'method': 'POST',
                    'path': '/api/register',
                    'description': 'Register new user (Admin only)',
                    'requires': 'manage_users'
                }
            },
            'customers': '/api/customers',
            'orders': '/api/orders',
            'products': '/api/products'
        }
    })

if __name__ == '__main__':
    app.run(debug=True)

