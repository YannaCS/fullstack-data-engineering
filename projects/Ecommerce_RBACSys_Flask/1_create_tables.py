#Create all RBAC tables
from create_app import create_app
from db import db
from models import *

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        print("Creating tables in 'ecommerce' schema...")
        db.create_all()
        print("✅ Tables created!")