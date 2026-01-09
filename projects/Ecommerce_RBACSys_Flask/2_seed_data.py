"""
Seed RBAC Data
- Create 9 permissions
- Create 3 roles (Admin, Sales, Viewer)
- Assign permissions to roles
- Create initial admin user
"""

from create_app import create_app
from db import db
from models import *
from werkzeug.security import generate_password_hash

def seed_rbac_data():
    print("Seeding RBAC data...")
    
    app = create_app()
    
    with app.app_context():
        # Check if data already exists
        existing_roles = db.session.query(Role).count()
        if existing_roles > 0:
            print("⚠️  Data already exists!")
            response = input("Clear and re-seed? (yes/no): ")
            if response.lower() != 'yes':
                print("Seeding cancelled.")
                return
            
            # Clear existing data (in correct order to avoid FK constraints)
            print("Clearing existing data...")
            db.session.query(RolePermission).delete()
            db.session.query(User).delete()
            db.session.query(Permission).delete()
            db.session.query(Role).delete()
            db.session.commit()
        
        # ===== 1. Create 9 Permissions =====
        print("\n📝 Creating permissions...")
        permissions_data = [
            ('view_customers', 'View customers list and details'),
            ('create_customers', 'Create new customers'),
            ('update_customers', 'Update customer information'),
            ('delete_customers', 'Delete customers'),
            ('view_orders', 'View orders list and details'),
            ('create_orders', 'Create new orders'),
            ('update_orders', 'Update order information'),
            ('delete_orders', 'Delete orders'),
            ('manage_users', 'Register new users and assign roles'),
        ]
        
        permissions = {}
        for name, desc in permissions_data:
            perm = Permission(name=name, description=desc)
            db.session.add(perm)
            permissions[name] = perm
            print(f"   ✓ {name}")
        
        db.session.flush()  # Get IDs without committing
        print(f"   ✅ Created {len(permissions)} permissions")
        
        # ===== 2. Create Roles with Permissions =====
        print("\n👥 Creating roles...")
        
        # Admin Role - ALL 9 permissions
        admin_role = Role(
            name='Admin',
            description='Full system access, can manage everything including user registration'
        )
        admin_role.permissions = list(permissions.values())  # All 9
        db.session.add(admin_role)
        print(f"   ✓ Admin: {len(admin_role.permissions)} permissions")
        
        # Sales Role - 6 permissions
        sales_role = Role(
            name='Sales',
            description='Can manage customers and orders, but cannot delete or manage users'
        )
        sales_role.permissions = [
            permissions['view_customers'],
            permissions['create_customers'],
            permissions['update_customers'],
            permissions['view_orders'],
            permissions['create_orders'],
            permissions['update_orders']
        ]
        db.session.add(sales_role)
        print(f"   ✓ Sales: {len(sales_role.permissions)} permissions")
        
        # Viewer Role - 2 permissions
        viewer_role = Role(
            name='Viewer',
            description='Read-only access to customers and orders'
        )
        viewer_role.permissions = [
            permissions['view_customers'],
            permissions['view_orders']
        ]
        db.session.add(viewer_role)
        print(f"   ✓ Viewer: {len(viewer_role.permissions)} permissions")
        
        db.session.flush()
        print(f"   ✅ Created 3 roles")
        
        # ===== 3. Create Initial Admin User =====
        print("\n🔐 Creating initial admin user...")
        admin_user = User(
            username='Admin User',
            email='admin@example.com',
            role=admin_role
        )
        admin_password = Password(
            user = admin_user,
            password_hash = generate_password_hash('Admin123')
        )
        db.session.add(admin_user)
        print(f"   ✓ {admin_user.email}")
        
        # Commit everything
        db.session.commit()
        
        print("\n" + "="*60)
        print("✅ RBAC Data Seeded Successfully!")
        print("="*60)
        print("\n📊 Summary:")
        print(f"   - Permissions: {len(permissions)}")
        print(f"   - Roles: 3 (Admin, Sales, Viewer)")
        print(f"   - Users: 1 (admin)")
        
        print("\n📋 Role-Permission Breakdown:")
        print(f"   Admin Role:")
        for perm in admin_role.permissions:
            print(f"      • {perm.name}")
        
        print(f"\n   Sales Role:")
        for perm in sales_role.permissions:
            print(f"      • {perm.name}")
        
        print(f"\n   Viewer Role:")
        for perm in viewer_role.permissions:
            print(f"      • {perm.name}")
        
        print("\n🔑 Initial Admin Credentials:")
        print("   Email:    admin@example.com")
        print("   Password: Admin123")
        print("\n⚠️  Remember to change the admin password after first login!")

if __name__ == '__main__':
    seed_rbac_data()