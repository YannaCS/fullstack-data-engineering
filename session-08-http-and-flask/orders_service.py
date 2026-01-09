from flask import Blueprint, jsonify, request
from models import db, Order, Customer
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from decimal import Decimal

orders_bp = Blueprint('orders', __name__, url_prefix='/api/orders')


@orders_bp.route('', methods=['GET'])
def get_all_orders():
    """Get all orders"""
    try:
        orders = db.session.execute(db.select(Order)).scalars().all()
        return jsonify([{
            'id': o.id,
            'customer_id': o.customer_id,
            'customer_name': o.customer.name if o.customer else None,
            'order_date': o.order_date.isoformat() if o.order_date else None,
            'total_amount': float(o.total_amount) if o.total_amount else 0,
            'status': o.status
        } for o in orders]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@orders_bp.route('/<int:id>', methods=['GET'])
def get_order(id):
    """Get single order by ID"""
    try:
        order = db.session.get(Order, id)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        return jsonify({
            'id': order.id,
            'customer_id': order.customer_id,
            'customer_name': order.customer.name if order.customer else None,
            'customer_email': order.customer.email if order.customer else None,
            'order_date': order.order_date.isoformat() if order.order_date else None,
            'total_amount': float(order.total_amount) if order.total_amount else 0,
            'status': order.status,
            'order_items': [{
                'id': item.id,
                'product_id': item.product_id,
                'product_name': item.product.name if item.product else None,
                'quantity': item.quantity,
                'unit_price': float(item.unit_price) if item.unit_price else 0
            } for item in order.order_items]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@orders_bp.route('', methods=['POST'])
def create_order():
    """Create new order"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        if not data.get('customer_id'):
            return jsonify({'error': 'customer_id is required'}), 400
        
        if not data.get('total_amount'):
            return jsonify({'error': 'total_amount is required'}), 400
        
        # Verify customer exists
        customer = db.session.get(Customer, data['customer_id'])
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        # Create order
        order = Order(
            customer_id=data['customer_id'],
            order_date=datetime.now(),
            total_amount=Decimal(str(data['total_amount'])),
            status=data.get('status', 'pending')
        )
        
        db.session.add(order)
        db.session.commit()
        
        return jsonify({
            'id': order.id,
            'customer_id': order.customer_id,
            'order_date': order.order_date.isoformat(),
            'total_amount': float(order.total_amount),
            'status': order.status,
            'message': 'Order created successfully'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': f'Invalid total_amount format: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@orders_bp.route('/<int:id>', methods=['PUT'])
def update_order(id):
    """Update order"""
    try:
        order = db.session.get(Order, id)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update fields if provided
        if 'customer_id' in data:
            # Verify customer exists
            customer = db.session.get(Customer, data['customer_id'])
            if not customer:
                return jsonify({'error': 'Customer not found'}), 404
            order.customer_id = data['customer_id']
        
        if 'total_amount' in data:
            try:
                order.total_amount = Decimal(str(data['total_amount']))
            except ValueError as e:
                return jsonify({'error': f'Invalid total_amount format: {str(e)}'}), 400
        
        if 'status' in data:
            # Validate status values
            valid_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
            if data['status'] not in valid_statuses:
                return jsonify({'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'}), 400
            order.status = data['status']
        
        if 'order_date' in data:
            order.order_date = datetime.fromisoformat(data['order_date'])
        
        db.session.commit()
        
        return jsonify({
            'id': order.id,
            'customer_id': order.customer_id,
            'order_date': order.order_date.isoformat(),
            'total_amount': float(order.total_amount),
            'status': order.status,
            'message': 'Order updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@orders_bp.route('/<int:id>', methods=['DELETE'])
def delete_order(id):
    """Delete order"""
    try:
        order = db.session.get(Order, id)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        db.session.delete(order)
        db.session.commit()
        
        return jsonify({'message': 'Order deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@orders_bp.route('/customer/<int:customer_id>', methods=['GET'])
def get_orders_by_customer(customer_id):
    """Get all orders for a specific customer"""
    try:
        # Verify customer exists
        customer = db.session.get(Customer, customer_id)
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        orders = db.session.execute(
            db.select(Order).where(Order.customer_id == customer_id)
        ).scalars().all()
        
        return jsonify([{
            'id': o.id,
            'customer_id': o.customer_id,
            'order_date': o.order_date.isoformat() if o.order_date else None,
            'total_amount': float(o.total_amount) if o.total_amount else 0,
            'status': o.status
        } for o in orders]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500