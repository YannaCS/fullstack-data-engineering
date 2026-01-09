from flask import Flask, Blueprint, jsonify, request
from models import db, Product

products_bp = Blueprint('products', __name__, url_prefix='/products')


@products_bp.route('/', methods=['GET'])
def products():
    products_res = db.session.execute(db.select(Product)).scalars().all()
    products = [x.to_dict() for x in products_res]

    return jsonify(products)

@products_bp.route('/<int:id>', methods=['GET'])
def get_product(id):
    res = db.session.execute(db.select(Product).where(Product.id == id)).scalars().first()
    if not res:
        return {"error": 'Not found'}, 404

    return jsonify(res.to_dict())

@products_bp.route('/', methods=['POST'])
def create_product():
    data = request.get_json()
    if not data or 'name' not in data or 'stock' not in data or 'price' not in data:
        return {"error": "Fields missing"}, 400
    try:
        product = Product(
            name=data['name'],
            price=data["price"],
            stock=data["stock"]
        )
        
        db.session.add(product)
        db.session.commit()
        return product.to_dict()
    except Exception as e:
        db.session.rollback()
        return {"error": "failed to create"}, 500
    
@products_bp.route('/<int:id>', methods=['PUT'])
def update_product(id):
    data = request.get_json()
    if not data:
        return {"error": "data missing"}, 400
    
    product = db.session.execute(db.select(Product).where(Product.id == id)).scalars().first()
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No update data provided'}), 400

    if 'name' in data:
        product.name = data['name']
    if 'price' in data:
        product.price = data['price']
    if 'stock' in data:
        product.stock = data['stock']
    try:
        db.session.commit()
        return jsonify({
            'id': product.id,
            'name': product.name,
            'price': float(product.price),
            'stock': product.stock
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
@products_bp.route('/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = db.session.execute(db.select(Product).where(Product.id == id)).scalars().first()
    if not product:
        return {"error": 'Not found'}, 404
    
    try:
        db.session.delete(product)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return {"error": 'failed to delete'}, 500
