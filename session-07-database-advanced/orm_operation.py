from engine import engine
from models import Customer, CustomerProfile, Product, Order, OrderItem
from sqlalchemy.orm import Session
from sqlalchemy import select, func



def create_customer_with_profile():
    with Session(engine) as session:
        with session.begin():
            customer = Customer(
                name="James Bond",
                email="JamesBound@example.com",
                profile=CustomerProfile(
                    phone="123456",
                    address="123 haha street",
                )
            )
            
            session.add(customer)
            print(f'customer {customer.name}is created')
            return customer.id

def get_customer_by_id(id):
    with Session(engine) as session:
        stmt = select(Customer).where(Customer.id == id)
        result = session.execute(stmt).scalar()
        if result:
            print(result.email, result.name)
        
def get_customer_order_stats():
    with Session(engine) as session:
        stmt = select(
            Customer.id,
            Customer.name,
            func.count(Order.id).label('order_count')
        ).join(Order).group_by(Customer.id, Customer.name)
        
        results = session.execute(stmt).all()
        print(results)
        
        return [
            {
                'id': r.id,
                'name': r.name,
                'order_count': r.order_count
            }
            for r in results
        ]
        
        
# get_customer_by_id(1)
# create_customer_with_profile()
print(get_customer_order_stats())