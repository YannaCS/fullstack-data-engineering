## Overview
Enhance your existing Customer and Order management API with a Role-Based Access Control (RBAC) system. Users will be assigned roles, and roles will have specific permissions that control access to customer and order operations.

---

## Database Schema Requirements

### 1. Users Table
Create a user model that stores:
- Basic user information (email, password hash, name)
- A **single role** assigned to each user (one-to-many relationship)

### 2. Roles Table
Create a role model that represents business functions:
- Role name
- Role description
- **Multiple permissions** associated with each role (many-to-many relationship)

### 3. Permissions Table
Create a permission model for specific operations:
- Permission name (see required permissions below)
- Permission description

### 4. Role-Permission Association
Create a **many-to-many** relationship between roles and permissions using an association/junction table.

---

## Required Permissions (9 Total)

### Customer Permissions
- `view_customers` - View customers (both list and details)
- `create_customers` - Create new customers
- `update_customers` - Update customer information
- `delete_customers` - Delete customers

### Order Permissions
- `view_orders` - View orders (both list and details)
- `create_orders` - Create new orders
- `update_orders` - Update order information
- `delete_orders` - Delete orders

### User Management Permission
- `manage_users` - Register new users and assign roles

---

## Required Roles with Permission Assignments

### 1. Admin Role
**Description**: Full system access, can manage everything including user registration

**Permissions**:
- `view_customers`
- `create_customers`
- `update_customers`
- `delete_customers`
- `view_orders`
- `create_orders`
- `update_orders`
- `delete_orders`
- `manage_users`

### 2. Sales Role
**Description**: Can manage customers and orders, but cannot delete or manage users

**Permissions**:
- `view_customers`
- `create_customers`
- `update_customers`
- `view_orders`
- `create_orders`
- `update_orders`

### 3. Viewer Role
**Description**: Read-only access to customers and orders

**Permissions**:
- `view_customers`
- `view_orders`

---

## API Endpoints with Required Permissions

### Authentication Endpoints (New Api)
```
POST   /api/login               → Public (no authentication required)
POST   /api/register            → Requires: manage_users (admin only!)
```

### Customer Endpoints
```
GET    /api/customers           → Requires: view_customers
GET    /api/customers/<id>      → Requires: view_customers
POST   /api/customers           → Requires: create_customers
PUT    /api/customers/<id>      → Requires: update_customers
DELETE /api/customers/<id>      → Requires: delete_customers
```

### Order Endpoints
```
GET    /api/orders              → Requires: view_orders
GET    /api/orders/<id>         → Requires: view_orders
POST   /api/orders              → Requires: create_orders
PUT    /api/orders/<id>         → Requires: update_orders
DELETE /api/orders/<id>         → Requires: delete_orders
```


## Implementation Requirements

### Phase 1: Database Setup
1. Create Users, Roles, Permissions, and Role-Permissions tables
2. Establish proper relationships:
   - Users → Roles (many-to-one)
   - Roles ↔ Permissions (many-to-many with junction table)

### Phase 2: Seed Data
Write a seed script that creates:

**Permissions**:
- `view_customers`
- `create_customers`
- `update_customers`
- `delete_customers`

- `view_orders`
- `create_orders`
- `update_orders`
- `delete_orders`

- `manage_users`

**Roles (3 total) with Permission Assignments**:
- **Admin**: All 9 permissions
- **Sales**: 6 permissions (view/create/update for customers and orders)
- **Viewer**: 2 permissions (view customers and orders)

**Initial Admin User** (important!):
- email: admin@example.com
- password: Admin123
- role: Admin

> **Note**: You MUST create at least one admin user in the seed script, otherwise no one can register new users!

### Phase 3: Authentication
1. **Login endpoint** (POST /api/login):
   - Public endpoint (no authentication required)
   - Accepts email and password
   - Returns JWT token on success
   - JWT must include: user_id, email, role_name, and list of permission names

2. **Register endpoint** (POST /api/register):
   - **Protected by `manage_users` permission** (admin only!)
   - Admin must be logged in to create new users
   - Admin specifies which role to assign to new user
   - Validate inputs with Pydantic

### Phase 4: Authorization System
1. Create `@permission_required(permission_name)` decorator
2. Apply permission decorator to ALL customer and order endpoints
3. Apply permission decorator to register endpoint (`manage_users`)
4. Decorator should:
   - Extract JWT from Authorization header
   - Decode JWT and get permissions list
   - Check if required permission is in user's permissions
   - Return 401 if no token, 403 if insufficient permissions

---

## Business Rules

1. **No Self-Registration**: Regular users cannot register themselves - only admins can create accounts
2. **Initial Admin**: Seed script must create at least one admin user
3. **Admin Creates Users**: Admin decides which role to assign when creating new users
4. **Cannot Delete Roles**: The three roles are fixed (Admin, Sales, Viewer)
5. **JWT Contains Permissions**: Include full permission list in JWT to avoid database lookups on every request

---
