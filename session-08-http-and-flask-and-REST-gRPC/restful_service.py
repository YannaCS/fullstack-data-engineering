from decimal import Decimal
from flask import Flask, jsonify, request
from models import db, Product

app = Flask(__name__)

app.config.from_object('db_config')

db.init_app(app)

@app.route('/')  # Root path
def home():
    return 'hello world'

@app.route('/products')
def products():
    products_res = db.session.execute(db.select(Product)).scalars().all()
    products = [x.to_dict() for x in products_res]

    return jsonify(products)

@app.route('/products/<int:id>', methods=['GET'])
def get_products(id):
    #res = db.session.execute(db.select(Product).where(Product.id == id)).scalars()
    res = db.session.get(Product, id)
    if not res:
        return {"error": "Not found"}, 404
    print(res)

    return jsonify(res.to_dict())

@app.route('/products', methods=['POST'])
def create_products():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Checks if key exists AND if value is truthy
        if not data.get('name'):
            return jsonify({"error": "name is required"}), 400
        
        if not data.get('price'):
            return jsonify({"error": "price is required"}), 400
        
        if not data.get('stock'):
            return jsonify({"error": "stock is required"}), 400
        
        # Create product
        product = Product(
            name=data['name'],
            price=Decimal(str(data['price'])),
            stock=data['stock']
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({
            **product.to_dict(),
            "message": "Product created successfully"
        }), 201
        
    except ValueError as e:
        return jsonify({"error": f"Invalid price format: {str(e)}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to create product"}), 500


if __name__ == '__main__':
    app.run(debug=True)

