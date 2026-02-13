from flask import Blueprint, jsonify, request
from models import db, Customer, CustomerProfile
from sqlalchemy.exc import IntegrityError
from datetime import datetime

customers_bp = Blueprint('customers', __name__, url_prefix='/api/customers')


@customers_bp.route('', methods=['GET'])
def get_all_customers():
    """Get all customers"""
    try:
        customers = db.session.execute(db.select(Customer)).scalars().all()
        return jsonify([{
            'id': c.id,
            'name': c.name,
            'email': c.email,
            'created_at': c.created_at.isoformat() if c.created_at else None
        } for c in customers]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@customers_bp.route('/<int:id>', methods=['GET'])
def get_customer(id):
    """Get single customer by ID"""
    try:
        customer = db.session.get(Customer, id)
        
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        return jsonify({
            'id': customer.id,
            'name': customer.name,
            'email': customer.email,
            'created_at': customer.created_at.isoformat() if customer.created_at else None,
            'profile': {
                'phone': customer.profile.phone,
                'address': customer.profile.address,
                'date_of_birth': customer.profile.date_of_birth.isoformat() if customer.profile and customer.profile.date_of_birth else None
            } if customer.profile else None
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@customers_bp.route('', methods=['POST'])
def create_customer():
    """Create new customer"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        if not data.get('name'):
            return jsonify({'error': 'Name is required'}), 400
        
        if not data.get('email'):
            return jsonify({'error': 'Email is required'}), 400
        
        # Create customer
        customer = Customer(
            name=data['name'],
            email=data['email'],
            created_at=datetime.now()
        )
        
        # Add optional profile if provided
        profile_data = data.get('profile')
        if profile_data:
            customer.profile = CustomerProfile(
                phone=profile_data.get('phone'),
                address=profile_data.get('address'),
                date_of_birth=datetime.fromisoformat(profile_data['date_of_birth']) if profile_data.get('date_of_birth') else None
            )
        
        db.session.add(customer)
        db.session.commit()
        
        return jsonify({
            'id': customer.id,
            'name': customer.name,
            'email': customer.email,
            'created_at': customer.created_at.isoformat(),
            'message': 'Customer created successfully'
        }), 201
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Email already exists'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@customers_bp.route('/<int:id>', methods=['PUT'])
def update_customer(id):
    """Update customer"""
    try:
        customer = db.session.get(Customer, id)
        
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update fields if provided
        if 'name' in data:
            customer.name = data['name']
        
        if 'email' in data:
            customer.email = data['email']
        
        # Update profile if provided
        if 'profile' in data:
            profile_data = data['profile']
            if customer.profile:
                # Update existing profile
                if 'phone' in profile_data:
                    customer.profile.phone = profile_data['phone']
                if 'address' in profile_data:
                    customer.profile.address = profile_data['address']
                if 'date_of_birth' in profile_data:
                    customer.profile.date_of_birth = datetime.fromisoformat(profile_data['date_of_birth']) if profile_data['date_of_birth'] else None
            else:
                # Create new profile
                customer.profile = CustomerProfile(
                    phone=profile_data.get('phone'),
                    address=profile_data.get('address'),
                    date_of_birth=datetime.fromisoformat(profile_data['date_of_birth']) if profile_data.get('date_of_birth') else None
                )
        
        db.session.commit()
        
        return jsonify({
            'id': customer.id,
            'name': customer.name,
            'email': customer.email,
            'message': 'Customer updated successfully'
        }), 200
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Email already exists'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@customers_bp.route('/<int:id>', methods=['DELETE'])
def delete_customer(id):
    """Delete customer"""
    try:
        customer = db.session.get(Customer, id)
        
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        db.session.delete(customer)
        db.session.commit()
        
        return jsonify({'message': 'Customer deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500