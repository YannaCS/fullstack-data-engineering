# Library Management System - Requirements Specification

## Overview
Design and implement a Library Management System that demonstrates OOP principles, design patterns, and Python best practices. The system manages books, DVDs, members, and borrowing operations.

---

## Functional Requirements

### FR1: Library Item Management
- **FR1.1**: Add library items (books and DVDs) with title, creator, and available copies (ID auto-generated)
- **FR1.2**: Remove library items from library
- **FR1.3**: Display all library items
- **FR1.4**: Search library items by title or creator

### FR2: Book Management
- **FR2.1**: Add books with title, author, ISBN, and number of pages

### FR3: DVD Management
- **FR3.1**: Add DVDs with title, director, duration, and genre

### FR4: Member Management
- **FR4.1**: Add members with name and email (member_id auto-generated)
- **FR4.2**: Remove members from library
- **FR4.3**: Display all members
- **FR4.4**: Support different member types (Regular, Premium) with different borrow limits

### FR5: Borrowing Operations
- **FR5.1**: Allow members to borrow library items (Regular: 3 items, Premium: 5 items)
- **FR5.2**: Allow members to return library items
- **FR5.3**: Show currently borrowed items by each member

### FR6: Waiting List & Notification System
- **FR6.1**: Allow members to join waiting list for unavailable items
- **FR6.2**: Remove members from waiting list
- **FR6.3**: Notify all waiting members when an item becomes available
- **FR6.4**: Display waiting list for a specific item

---

## Class Design

### 1. LibraryItem (Abstract Base Class)

**Attributes:**
- `id: int` - Auto-generated ID (1, 2, 3, ...)
- `title: str` - Title of the item
- `creator: str` - Author for books, Director for DVDs
- `total_copies: int` - Total number of copies
- `available_copies: int` - Number of available copies
- `_id_counter: int` - Class variable for auto-increment

**Methods:**
- `__init__(title, creator, copies)` - Constructor
- `is_available() -> bool` - Check if item is available
- `borrow() -> bool` - Borrow the item
- `return_item() -> bool` - Return the item
- `get_item_info() -> str` - Abstract method to be overridden
- `get_item_type() -> str` - Abstract method to be overridden
- `__str__() -> str` - String representation
- `__eq__(other) -> bool` - Compare by ID

---

### 2. Book (inherits LibraryItem)

**Attributes:**
- `author: str` - Author name (alias for creator)
- `isbn: str` - ISBN number
- `num_pages: int` - Number of pages

**Methods:**
- `__init__(title, author, copies, isbn, num_pages)` - Constructor
- `get_item_type() -> str` - Returns "Book"
- `get_item_info() -> str` - Override to include book details

---

### 3. DVD (inherits LibraryItem)

**Attributes:**
- `director: str` - Director name (alias for creator)
- `duration_minutes: int` - Duration in minutes
- `genre: str` - Genre of the DVD

**Methods:**
- `__init__(title, director, copies, duration_minutes, genre)` - Constructor
- `get_item_type() -> str` - Returns "DVD"
- `get_item_info() -> str` - Override to include DVD details

---

### 4. Member (Base Class - Observer)

**Attributes:**
- `member_id: int` - Auto-generated ID (1, 2, 3, ...)
- `name: str` - Member name
- `email: str` - Member email
- `borrowed_items: List[int]` - List of borrowed item IDs
- `notifications: List[str]` - List of notification messages
- `MAX_BORROW_LIMIT: int` - To be set by subclasses
- `_id_counter: int` - Class variable for auto-increment

**Methods:**
- `__init__(name, email)` - Constructor
- `can_borrow() -> bool` - Check if member can borrow more items
- `borrow_item(item_id: int) -> bool` - Borrow an item
- `return_item(item_id: int) -> bool` - Return an item
- `get_borrowed_count() -> int` - Get number of borrowed items
- `get_max_borrow_limit() -> int` - Abstract method to be overridden
- `update(message: str) -> None` - Observer method - receives notifications
- `get_notifications() -> List[str]` - Get all notifications
- `clear_notifications() -> None` - Clear all notifications
- `__str__() -> str` - String representation

---

### 5. RegularMember (inherits Member)

**Attributes:**
- `MAX_BORROW_LIMIT: int = 3` - Maximum 3 items

**Methods:**
- `__init__(name, email)` - Constructor
- `get_max_borrow_limit() -> int` - Returns 3

---

### 6. PremiumMember (inherits Member)

**Attributes:**
- `MAX_BORROW_LIMIT: int = 5` - Maximum 5 items
- `membership_expiry: str` - Optional expiry date

**Methods:**
- `__init__(name, email, membership_expiry=None)` - Constructor
- `get_max_borrow_limit() -> int` - Returns 5

---

### 7. Library (Singleton + Subject/Observable)

**Attributes:**
- `_instance: Library` - Singleton instance
- `items: Dict[int, LibraryItem]` - item_id → LibraryItem mapping
- `members: Dict[int, Member]` - member_id → Member mapping
- `waiting_list: Dict[int, List[Member]]` - item_id → List of waiting Members

**Methods:**
- `__new__(cls) -> Library` - Singleton pattern implementation
- `add_item(item: LibraryItem) -> bool` - Add item to library
- `remove_item(item_id: int) -> bool` - Remove item from library
- `add_member(member: Member) -> bool` - Add member to library
- `remove_member(member_id: int) -> bool` - Remove member from library
- `borrow_item(member_id: int, item_id: int) -> bool` - Borrow an item
- `return_item(member_id: int, item_id: int) -> bool` - Return an item
- `search_items(query: str) -> List[LibraryItem]` - Search items by title or creator
- `display_all_items() -> None` - Display all items
- `display_all_members() -> None` - Display all members
- `join_waiting_list(member_id: int, item_id: int) -> bool` - Join waiting list
- `leave_waiting_list(member_id: int, item_id: int) -> bool` - Leave waiting list
- `get_waiting_list(item_id: int) -> List[Member]` - Get waiting list for an item
- `notify_waiting_members(item_id: int) -> None` - Notify all waiting members
- `__len__() -> int` - Returns total number of items

---

## OOP Concepts Demonstrated

### Magic Methods
- `__init__` - Constructor with auto-generated IDs
- `__str__` - String representation
- `__eq__` - Equality comparison
- `__len__` - Return count
- `__new__` - Singleton pattern

### Four Pillars of OOP
1. **Encapsulation** - Private data with getter methods, class variables for ID counters
2. **Abstraction** - LibraryItem as abstract base class with abstract methods
3. **Inheritance** - LibraryItem → Book/DVD, Member → RegularMember/PremiumMember
4. **Polymorphism** - Method overriding (get_item_info, get_item_type, get_max_borrow_limit)

### Design Patterns
- **Singleton Pattern** - Library class (only one instance exists)
- **Observer Pattern** - Members on waiting list get notified when item becomes available

### SOLID Principles
- **Single Responsibility** - Each class has one clear purpose
- **Open/Closed** - Can extend with new item/member types without modifying existing code
- **Liskov Substitution** - Subclasses can replace base classes without breaking functionality

---

## Sample Usage
```python
def main():
    print("=" * 70)
    print("LIBRARY MANAGEMENT SYSTEM - DEMO")
    print("=" * 70)
    
    # Create library (Singleton)
    library = Library()
    
    # Add books and DVDs
    book1 = Book("Python Crash Course", "Eric Matthes", 2, "978-1593279288", 544)
    book2 = Book("Clean Code", "Robert Martin", 2, "978-0132350884", 464)
    dvd1 = DVD("The Matrix", "Wachowski Brothers", 2, 136, "Sci-Fi")
    dvd2 = DVD("Inception", "Christopher Nolan", 1, 148, "Thriller")
    
    library.add_item(book1)
    library.add_item(book2)
    library.add_item(dvd1)
    library.add_item(dvd2)
    
    print(f"\n--- Added Items ---")
    print(f"Book: {book1} (ID: {book1.id})")
    print(f"DVD: {dvd1} (ID: {dvd1.id})")
    print(f"Total items: {len(library)}")
    
    # Demonstrate Polymorphism - get_item_info()
    print(f"\n--- Polymorphism Demo: get_item_info() ---")
    print(book1.get_item_info())
    print(f"\n{dvd1.get_item_info()}")
    
    # Add members
    alice = RegularMember("Alice", "alice@email.com")
    bob = PremiumMember("Bob", "bob@email.com")
    charlie = RegularMember("Charlie", "charlie@email.com")
    
    library.add_member(alice)
    library.add_member(bob)
    library.add_member(charlie)
    
    print(f"\n--- Added Members ---")
    print(f"{alice} - Max: {alice.get_max_borrow_limit()} items")
    print(f"{bob} - Max: {bob.get_max_borrow_limit()} items")
    
    # Regular member borrows items (max 3)
    print(f"\n--- Regular Member Borrowing (Max 3) ---")
    library.borrow_item(alice.member_id, book1.id)
    library.borrow_item(alice.member_id, dvd1.id)
    library.borrow_item(alice.member_id, book2.id)
    print(f"Alice borrowed: {alice.get_borrowed_count()}/{alice.get_max_borrow_limit()} items")
    
    # Try to exceed limit
    success = library.borrow_item(alice.member_id, dvd2.id)
    print(f"Alice trying 4th item: {success} (exceeded limit)")
    
    # Premium member borrows items (max 5)
    print(f"\n--- Premium Member Borrowing (Max 5) ---")
    library.borrow_item(bob.member_id, dvd2.id)
    print(f"Bob borrowed: {bob.get_borrowed_count()}/{bob.get_max_borrow_limit()} items")
    print(f"'{dvd2.title}' available: {dvd2.available_copies}")
    
    # Waiting list and Observer pattern
    print(f"\n--- Waiting List & Observer Pattern ---")
    success = library.borrow_item(charlie.member_id, dvd2.id)
    print(f"Charlie trying to borrow '{dvd2.title}': {success} (unavailable)")
    
    library.join_waiting_list(charlie.member_id, dvd2.id)
    print(f"Charlie joined waiting list")
    print(f"Waiting list size: {len(library.get_waiting_list(dvd2.id))}")
    
    # Return item - triggers notification
    print(f"\nBob returns '{dvd2.title}'...")
    library.return_item(bob.member_id, dvd2.id)
    print(f"Charlie's notifications: {charlie.get_notifications()}")
    
    # Search functionality
    print(f"\n--- Search Items ---")
    results = library.search_items("Python")
    print(f"Search 'Python': {len(results)} result(s)")
    
    results = library.search_items("Matrix")
    print(f"Search 'Matrix': {len(results)} result(s)")
    
    # Display final state
    print(f"\n--- Final State ---")
    print(f"Total items: {len(library)}")
    library.display_all_items()
    
    print("\n" + "=" * 70)
    print("DEMO COMPLETED!")
    print("=" * 70)


if __name__ == "__main__":
    main()
```

---

## Expected Output
```
======================================================================
LIBRARY MANAGEMENT SYSTEM - DEMO
======================================================================

--- Added Items ---
Book: Python Crash Course by Eric Matthes (ID: 1)
DVD: The Matrix by Wachowski Brothers (ID: 3)
Total items: 4

--- Polymorphism Demo: get_item_info() ---
Title: Python Crash Course
Author: Eric Matthes
ISBN: 978-1593279288
Pages: 544
Type: Book

Title: The Matrix
Director: Wachowski Brothers
Duration: 136 minutes
Genre: Sci-Fi
Type: DVD

--- Added Members ---
Alice (1) - Max: 3 items
Bob (2) - Max: 5 items

--- Regular Member Borrowing (Max 3) ---
Alice borrowed: 3/3 items
Alice trying 4th item: False (exceeded limit)

--- Premium Member Borrowing (Max 5) ---
Bob borrowed: 1/5 items
'Inception' available: 0

--- Waiting List & Observer Pattern ---
Charlie trying to borrow 'Inception': False (unavailable)
Charlie joined waiting list
Waiting list size: 1

Bob returns 'Inception'...
Charlie's notifications: ["'Inception' is now available!"]

--- Search Items ---
Search 'Python': 1 result(s)
Search 'Matrix': 1 result(s)

--- Final State ---
Total items: 4
[Display all items]

======================================================================
DEMO COMPLETED!
======================================================================
```

---

## Estimated Completion Time
**1.5 - 2 hours**

## Deliverables
- Implementation of all 7 classes
- Demonstration of all OOP concepts
- Working sample usage code
- Proper documentation and comments