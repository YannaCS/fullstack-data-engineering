# ORM - Object relation Mapping
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Text, Date
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

class Base (DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)


class Customer(db.Model):
    __tablename__ = 'customers'
    
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
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), unique=True, nullable=False)
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
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
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
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    
    # Relationships
    order = relationship('Order', back_populates='order_items')
    product = relationship('Product', back_populates='order_items')
    
    def __repr__(self):
        return f"<OrderItem(order_id={self.order_id}, product_id={self.product_id}, quantity={self.quantity})>"
