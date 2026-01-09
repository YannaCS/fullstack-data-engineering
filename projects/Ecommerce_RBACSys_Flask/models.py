# ORM - Object relation Mapping
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Text, Date
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from db import db

class Role(db.Model):
    __tablename__  = 'roles'
    __table_args__ = {'schema': 'ecommerce'}

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    # One role can have many users
    users = relationship('User', back_populates='role')
    # Many-to-many relationship with permissions through junction table
    permissions = relationship('Permission',
                               secondary='ecommerce.role_permissions',
                               back_populates='roles')
    

class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'ecommerce'}
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    role_id = Column(Integer, ForeignKey('ecommerce.roles.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    # One-to-one relationship to Password
    password = relationship('Password', 
                           uselist=False, 
                           back_populates='user',
                           cascade='all, delete-orphan')
    # User many-to-one Role
    role = relationship('Role', back_populates='users')
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', role='{self.role}')>"

# Password model (1-to-1 with User)
class Password(db.Model):
    __tablename__ = 'passwords'
    __table_args__ = {'schema': 'ecommerce'}
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('ecommerce.users.id'), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Relationship back to User
    user = relationship('User', back_populates='password')
    
    def __repr__(self):
        return f"<Password(user_id={self.user_id})>"



class Permission(db.Model):
    __tablename__ = 'permissions'
    __table_args__ = {'schema': 'ecommerce'}

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255))
    created_at = Column(DateTime, default=datetime.now)

    # Relationship
    # Many-to-many with roles
    roles = relationship('Role', 
                         secondary='ecommerce.role_permissions',
                         back_populates='permissions')


class RolePermission(db.Model):
    __tablename__ = 'role_permissions'
    # Unique constraint to prevent duplicate assignments
    __table_args__ = (
        db.UniqueConstraint('role_id', 'permission_id', name='unique_role_permission'),
        {'schema': 'ecommerce'}
    )

    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey('ecommerce.roles.id'), nullable=False)
    permission_id = Column(Integer, ForeignKey('ecommerce.permissions.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

class Customer(db.Model):
    __tablename__ = 'customers'
    __table_args__ = {'schema': 'ecommerce'}

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=True)
    email = Column(String(255), unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    
    ## Relationship
    
    profile = relationship('CustomerProfile', back_populates='customer', uselist=False, cascade='all, delete-orphan')
    orders = relationship('Order', back_populates='customer', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Customer id={self.id} name={self.name}>"

class CustomerProfile(db.Model):
    __tablename__ = 'customer_profiles'
    __table_args__ = {'schema': 'ecommerce'}

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('ecommerce.customers.id'), unique=True, nullable=False)
    phone = Column(String(20))
    address = Column(Text)
    date_of_birth = Column(Date)
    
    # Relationship (back reference to customer)
    customer = relationship('Customer', back_populates='profile')
    
    def __repr__(self):
        return f"<CustomerProfile(customer_id={self.customer_id}, phone='{self.phone}')>"


# ========== Model 3: Product ==========
class Product(db.Model):
    __tablename__ = 'products'
    __table_args__ = {'schema': 'ecommerce'}

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, default=0)
    
    # Relationship
    order_items = relationship('OrderItem', back_populates='product')
    
    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price=${self.price}, stock={self.stock})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "stock": self.stock
        }


# ========== Model 4: Order (1-to-many with Customer) ==========
class Order(db.Model):
    __tablename__ = 'orders'
    __table_args__ = {'schema': 'ecommerce'}

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('ecommerce.customers.id'), nullable=False)
    order_date = Column(DateTime, default=datetime.now)
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(50), default='pending')
    
    # Relationships
    customer = relationship('Customer', back_populates='orders')
    order_items = relationship('OrderItem', back_populates='order', 
                              cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Order(id={self.id}, customer_id={self.customer_id}, total=${self.total_amount}, status='{self.status}')>"


# ========== Model 5: OrderItem (Many-to-many junction) ==========
class OrderItem(db.Model):
    __tablename__ = 'order_items'
    __table_args__ = {'schema': 'ecommerce'}

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('ecommerce.orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('ecommerce.products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    
    # Relationships
    order = relationship('Order', back_populates='order_items')
    product = relationship('Product', back_populates='order_items')
    
    def __repr__(self):
        return f"<OrderItem(order_id={self.order_id}, product_id={self.product_id}, quantity={self.quantity})>"