# Library Management System - Database Integration

## Overview
Extend the Library Management System from Session 4 to integrate with a PostgreSQL database using SQLAlchemy. You will design the database schema, implement SQLAlchemy models, and connect them with the existing OOP classes.
```
User Code
    ↓
Library (business logic + Observer pattern)
    ↓
DatabaseManager (CRUD operations)
    ↓
SQLAlchemy Models
    ↓
PostgreSQL Database
```
---

## Prerequisites
- Completed Library Management System from Session 4
- PostgreSQL installed and running locally
- SQLAlchemy installed (`pip install sqlalchemy psycopg2-binary`)

---

## Part 1: Database Schema Design

### Requirements

Design a relational database schema that supports all the functionality of the Library Management System. Your schema must include:

1. **library_items table** - Stores all library items (books and DVDs)
2. **books table** - Stores book-specific information
3. **dvds table** - Stores DVD-specific information
4. **members table** - Stores member information
5. **memberships table** - Stores membership types and limits
6. **borrowed_items table** - Tracks borrowing transactions
7. **waiting_list table** - Tracks members waiting for items
8. **notifications table** - Stores member notifications

### Schema Specifications

#### 1. library_items
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Item ID |
| title | VARCHAR(255) | NOT NULL | Item title |
| creator | VARCHAR(255) | NOT NULL | Author/Director |
| item_type | VARCHAR(20) | NOT NULL | 'book' or 'dvd' |
| total_copies | INTEGER | NOT NULL, DEFAULT 1 | Total copies |
| available_copies | INTEGER | NOT NULL, DEFAULT 1 | Available copies |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation time |

#### 2. books
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, FOREIGN KEY → library_items(id) | Book ID |
| isbn | VARCHAR(20) | NOT NULL, UNIQUE | ISBN number |
| num_pages | INTEGER | NOT NULL | Number of pages |

#### 3. dvds
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, FOREIGN KEY → library_items(id) | DVD ID |
| duration_minutes | INTEGER | NOT NULL | Duration in minutes |
| genre | VARCHAR(50) | NOT NULL | Genre |

#### 4. members
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Member ID |
| name | VARCHAR(255) | NOT NULL | Member name |
| email | VARCHAR(255) | NOT NULL, UNIQUE | Member email |
| membership_id | INTEGER | NOT NULL, FOREIGN KEY → memberships(id) | Membership type ID |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation time |

#### 5. memberships
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Membership ID |
| member_id | INTEGER | NOT NULL, UNIQUE | Member ID |
| membership_type | VARCHAR(20) | NOT NULL | 'regular' or 'premium' |
| borrow_limit | INTEGER | NOT NULL | Maximum items that can be borrowed |
| expiry_date | DATE | NULL | Expiry date (NULL for regular, required for premium) |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update time |

#### 6. borrowed_items
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Transaction ID |
| member_id | INTEGER | NOT NULL, FOREIGN KEY → members(id) | Member ID |
| item_id | INTEGER | NOT NULL, FOREIGN KEY → library_items(id) | Item ID |
| borrow_date | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Borrow date |
| return_date | TIMESTAMP | NULL | Return date (NULL if not returned) |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'borrowed' | 'borrowed' or 'returned' |

#### 7. waiting_list
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Waiting list ID |
| member_id | INTEGER | NOT NULL, FOREIGN KEY → members(id) | Member ID |
| item_id | INTEGER | NOT NULL, FOREIGN KEY → library_items(id) | Item ID |
| joined_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Join time |
| UNIQUE(member_id, item_id) | - | UNIQUE constraint | Prevent duplicate entries |

#### 8. notifications
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Notification ID |
| member_id | INTEGER | NOT NULL, FOREIGN KEY → members(id) | Member ID |
| message | TEXT | NOT NULL | Notification message |
| is_read | BOOLEAN | DEFAULT FALSE | Read status |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation time |

### Deliverable 1: Create `schema.sql`
Write SQL DDL statements to create all tables with proper constraints, and relationships. Include CREATE TABLE statements, foreign keys.

---

## Part 2: SQLAlchemy Models

### Requirements

Create SQLAlchemy ORM models that map to your database schema. Your models should:

1. Use declarative base mapping
2. Define proper relationships between tables
3. Include appropriate cascade options
4. Implement useful methods for common operations

### Model Specifications

#### 1. LibraryItemModel
- Maps to `library_items` table
- Relationships:
  - One-to-one with `BookModel` or `DVDModel`
  - One-to-many with `BorrowedItemModel`
  - One-to-many with `WaitingListModel`
- Methods:
  - `is_available() -> bool`
  - `get_active_borrows() -> List[BorrowedItemModel]`

#### 2. BookModel
- Maps to `books` table
- Relationships:
  - One-to-one with `LibraryItemModel`

#### 3. DVDModel
- Maps to `dvds` table
- Relationships:
  - One-to-one with `LibraryItemModel`

#### 4. MemberModel
- Maps to `members` table
- Relationships:
  - One-to-one with `MembershipModel`
  - One-to-many with `BorrowedItemModel`
  - One-to-many with `WaitingListModel`
  - One-to-many with `NotificationModel`
- Methods:
  - `get_borrowed_count() -> int`
  - `can_borrow() -> bool`
  - `get_borrow_limit() -> int` (delegates to membership)

#### 5. MembershipModel
- Maps to `memberships` table
- Relationships:
  - One-to-one with `MemberModel`
- Methods:
  - `is_expired() -> bool`
  - `days_until_expiry() -> int`
  - `renew(days: int) -> None`

#### 6. BorrowedItemModel
- Maps to `borrowed_items` table
- Relationships:
  - Many-to-one with `MemberModel`
  - Many-to-one with `LibraryItemModel`

#### 7. WaitingListModel
- Maps to `waiting_list` table
- Relationships:
  - Many-to-one with `MemberModel`
  - Many-to-one with `LibraryItemModel`

#### 8. NotificationModel
- Maps to `notifications` table
- Relationships:
  - Many-to-one with `MemberModel`

### Deliverable 2: Create `models.py`
Implement all SQLAlchemy models with:
- Column definitions matching your schema
- Relationship definitions with proper `back_populates`
- Cascade options for delete operations
- Helper methods for each model as specified above

---

## Part 3: Database Operations Layer

### Requirements

Create a database operations layer that integrates with your existing Library Management System. This layer should handle all database CRUD operations.

Key Concepts:
1. session.add(obj) - Stages object for insertion (not yet in DB)
2. session.flush() - Sends to DB to get auto-generated IDs, but doesn't commit
3. session.commit() - Permanently saves all changes (happens automatically in context manager)
4. session.rollback() - Undoes all changes if error occurs
5. session.expunge(obj) - Detaches object from session so it can be used outside the with block
6. Transactions - All operations in a with block succeed together or fail together  


### DatabaseManager Class

Create a `DatabaseManager` class (Singleton pattern) that:
1. Manages database connection and session
2. Provides methods for all library operations
3. Handles transactions and error handling
4. Uses context managers for session management

### Key Methods to Implement:

#### Item Operations
- `add_book(title, author, copies, isbn, num_pages) -> BookModel`
- `add_dvd(title, director, copies, duration, genre) -> DVDModel`
- `remove_item(item_id: int) -> bool`
- `get_item_by_id(item_id: int) -> LibraryItemModel`
- `search_items(query: str) -> List[LibraryItemModel]`
- `get_all_items() -> List[LibraryItemModel]`

#### Member Operations
- `add_member(name, email, member_type, borrow_limit, expiry=None) -> MemberModel`
- `remove_member(member_id: int) -> bool`
- `get_member_by_id(member_id: int) -> MemberModel`
- `get_all_members() -> List[MemberModel]`

#### Membership Operations
- `create_membership(member_id, membership_type, borrow_limit, expiry=None) -> MembershipModel`
- `update_membership(member_id, membership_type=None, borrow_limit=None, expiry=None) -> bool`
- `renew_membership(member_id, days) -> bool`
- `get_membership(member_id: int) -> MembershipModel`
- `check_membership_expiry(member_id: int) -> bool`

#### Borrowing Operations
- `borrow_item(member_id: int, item_id: int) -> bool`
- `return_item(member_id: int, item_id: int) -> bool`
- `get_member_borrowed_items(member_id: int) -> List[LibraryItemModel]`
- `get_item_borrow_history(item_id: int) -> List[BorrowedItemModel]`

#### Waiting List Operations
- `join_waiting_list(member_id: int, item_id: int) -> bool`
- `leave_waiting_list(member_id: int, item_id: int) -> bool`
- `get_waiting_list(item_id: int) -> List[MemberModel]`
- `notify_waiting_members(item_id: int) -> None`

#### Notification Operations
- `create_notification(member_id: int, message: str) -> NotificationModel`
- `get_member_notifications(member_id: int, unread_only=False) -> List[NotificationModel]`
- `mark_notification_read(notification_id: int) -> bool`

### Deliverable 3: Create `database_manager.py`
Implement the DatabaseManager class with:
- Singleton pattern implementation
- Database connection and engine setup
- Session management with context managers
- All CRUD methods listed above
- Proper error handling and transaction rollback

---

## Part 4: Integration with OOP Classes

### Requirements

Integrate the database layer with your existing Library Management System classes from Session 4 using a **Pure ORM Approach**:
- Replace in-memory storage with database queries
- Modify existing classes to work directly with SQLAlchemy models
- Keep the same public interface so existing code still works
- All operations should persist to database automatically

### Strategy

Instead of maintaining separate OOP classes and database models, your classes will work directly with SQLAlchemy ORM objects. The key is to:
1. Have the `Library` class work with database sessions for all operations
2. Remove class-level ID counters (use database auto-increment instead)
3. Replace in-memory dictionaries with database queries
4. Maintain the same methods and interfaces for backward compatibility

### Integration Guidelines

#### 1. Library Class (Singleton + Database)
**What to Change:**
- Remove `items` and `members` dictionaries
- Add `DatabaseManager` instance
- Replace all dictionary operations with database queries
- Maintain Singleton pattern
- Keep all original methods (`add_item`, `borrow_item`, `return_item`, etc.)

**Key Responsibilities:**
- Manage all library operations through DatabaseManager
- Handle business logic (borrow limits, availability checks)
- Coordinate between different database tables
- Maintain Observer pattern for notifications

#### 2. Book and DVD Classes
**What to Change:**
- Create wrapper classes around SQLAlchemy models
- Constructor should immediately persist to database
- Provide properties to access database model attributes
- Maintain original interface (`title`, `author`/`director`, `get_item_info()`, etc.)

**Two Approaches:**
- **Option 1**: Factory functions that return database models
- **Option 2**: Wrapper classes with properties that delegate to database models (recommended)

#### 3. Member Classes
**What to Change:**
- Remove in-memory `borrowed_items` list - query from database
- Remove in-memory `notifications` list - query from database
- Create membership record automatically with member
- Query borrow limit from membership table

**Key Responsibilities:**
- `get_borrowed_count()` - query active borrows from database
- `get_max_borrow_limit()` - get limit from membership table
- `get_notifications()` - fetch from notifications table
- `update(message)` - implement Observer pattern with database persistence

**Subclasses:**
- `RegularMember` - creates member with 3-item borrow limit
- `PremiumMember` - creates member with 5-item borrow limit and optional expiry date

### Deliverable 4: Create `library_integrated.py`

Create a complete integration file that includes:
- `Library` class with DatabaseManager integration
- `Book` and `DVD` wrapper classes
- `Member`, `RegularMember`, and `PremiumMember` classes
- All classes maintain original Session 4 interface
- All operations persist to database
- Proper error handling

### Testing Your Integration

Ensure your integrated system:
1. ✅ Creates database records when objects are instantiated
2. ✅ All borrow/return operations persist to database
3. ✅ Search and display methods query from database
4. ✅ Waiting list and notifications work with database
5. ✅ Same public interface as original OOP system
6. ✅ Can restart the program and data persists

---

## Part 5: Testing & Demo

### Requirements

Create a comprehensive demo that:
1. Initializes the database (drop and recreate tables)
2. Creates sample data (books, DVDs, members)
3. Demonstrates all CRUD operations
4. Shows borrowing and returning workflow
5. Demonstrates waiting list and notifications
6. Verifies data persistence across program restarts

### Test Scenarios to Include:

#### 1. Database Initialization
- Drop all existing tables
- Recreate tables from schema
- Verify clean slate

#### 2. Sample Data Creation
- Add multiple books with different properties
- Add multiple DVDs with different genres
- Create regular and premium members
- Verify all records in database

#### 3. Borrowing Workflow
- Member borrows items
- Verify borrow limits (regular: 3, premium: 5)
- Check available copies decrease
- Query borrowed items from database

#### 4. Returning Workflow
- Member returns items
- Verify available copies increase
- Check borrow records updated
- Test notification system

#### 5. Waiting List
- Try to borrow unavailable item
- Join waiting list
- Return item triggers notifications
- Verify notifications in database

#### 6. Membership Management
- Check membership expiry
- Test borrow limit enforcement
- Renew premium membership

### Sample Test Script

Below is an example of how you might structure your demo script:

```python
from library_integrated import Library, Book, DVD, RegularMember, PremiumMember
from database_manager import DatabaseManager

def main():
    print("=" * 70)
    print("LIBRARY MANAGEMENT SYSTEM - DATABASE INTEGRATION DEMO")
    print("=" * 70)
    
    # Create library (Singleton)
    library = Library()
    
    # Add books and DVDs
    book1 = Book("Python Crash Course", "Eric Matthes", 2, "978-1593279288", 544)
    book2 = Book("Clean Code", "Robert Martin", 1, "978-0132350884", 464)
    dvd1 = DVD("The Matrix", "Wachowski Brothers", 1, 136, "Sci-Fi")
    
    library.add_item(book1)
    library.add_item(book2)
    library.add_item(dvd1)
    
    print(f"\n--- Added Items to Database ---")
    print(f"Total items in library: {len(library)}")
    
    # Add members
    alice = RegularMember("Alice", "alice@email.com")
    bob = PremiumMember("Bob", "bob@email.com", "2025-12-31")
    
    library.add_member(alice)
    library.add_member(bob)
    
    print(f"\n--- Added Members ---")
    print(f"Alice (Regular): Max {alice.get_max_borrow_limit()} items")
    print(f"Bob (Premium): Max {bob.get_max_borrow_limit()} items")
    
    # Test borrowing
    print(f"\n--- Testing Borrow Operations ---")
    library.borrow_item(alice.member_id, book1.id)
    print(f"Alice borrowed '{book1.title}'")
    print(f"Alice's borrowed count: {alice.get_borrowed_count()}")
    
    # Test waiting list
    print(f"\n--- Testing Waiting List ---")
    library.borrow_item(bob.member_id, dvd1.id)
    success = library.borrow_item(alice.member_id, dvd1.id)
    print(f"Alice tries to borrow '{dvd1.title}': {success}")
    
    library.join_waiting_list(alice.member_id, dvd1.id)
    print(f"Alice joined waiting list for '{dvd1.title}'")
    
    # Test return and notifications
    print(f"\n--- Testing Return & Notifications ---")
    library.return_item(bob.member_id, dvd1.id)
    print(f"Bob returned '{dvd1.title}'")
    
    notifications = alice.get_notifications()
    print(f"Alice's notifications: {notifications}")
    
    print("\n" + "=" * 70)
    print("DEMO COMPLETED!")
    print("=" * 70)

if __name__ == "__main__":
    main()
```

### Expected Output

```
======================================================================
LIBRARY MANAGEMENT SYSTEM - DATABASE INTEGRATION DEMO
======================================================================

--- Added Items to Database ---
Total items in library: 3

--- Added Members ---
Alice (Regular): Max 3 items
Bob (Premium): Max 5 items

--- Testing Borrow Operations ---
Alice borrowed 'Python Crash Course'
Alice's borrowed count: 1

--- Testing Waiting List ---
Alice tries to borrow 'The Matrix': False
Alice joined waiting list for 'The Matrix'

--- Testing Return & Notifications ---
Bob returned 'The Matrix'
Alice's notifications: ["'The Matrix' is now available!"]

======================================================================
DEMO COMPLETED!
======================================================================
```

---

## Estimated Completion Time
**3 - 4 hours**

## Deliverables Summary
1. `schema.sql` - Database schema DDL statements
2. `models.py` - SQLAlchemy ORM models with relationships
3. `database_manager.py` - Database operations layer (Singleton)
4. `library_integrated.py` - Integrated Library system with wrapper classes

---
