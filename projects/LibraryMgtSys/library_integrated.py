from abc import ABC, abstractclassmethod
from typing import List, Dict, Optional
from database_manager import DatabaseManager
from models import LibraryItemModel, BookModel, DVDModel, MemberModel, MembershipModel
from datetime import date, datetime

# -------------------------------
# LibraryItem (Abstract Base Class)
# -------------------------------
class LibraryItem(ABC):
    """
    Wrapper class around LibraryItemModel.
    Provides the same interface as before, but works with database.
    No need of _id_counter anymore because the database handles ID generation
    """
   
    def __init__(self, title: str, creator: str, total_copies: int):
        """
        Initialize with existing database ID.
        Called by Book/DVD after they create the DB record.
        """
        self.title = title
        self.creator = creator
        self.total_copies = total_copies
        # self.available_copies = total_copies # out of sync of database if the item is borrowed/returned after created
        self.db = DatabaseManager()
        # ID will be set by subclass after database insertion
        self.id = None

    @property
    def available_copies(self) -> int:
        """Always get current available copies from database"""
        if self.id is None:
            return 0
        item = self.db.get_item_by_id(self.id)
        return item.available_copies if item else 0

    def __str__(self) -> str:
        return f'{self.title} by {self.creator}'
    
    def __eq__(self, other) -> bool:
        if isinstance(other, LibraryItem):
            return self.id == other.id
        return False
    
    def is_available(self) -> bool:
        return self.available_copies > 0
    
    # These methods are no longer needed
    # Library handles borrow/return via DatabaseManager
    # But keep them for backward compatibility
    # def borrow(self) -> bool:
    #     """Deprecated: Use Library.borrow_item() instead"""
    #     if self.is_available():
    #         self.available_copies -= 1
    #         return True
    #     return False
    
    # def return_item(self) -> bool:
    #     """Deprecated: Use Library.return_item() instead"""
    #     if self.available_copies < self.total_copies:
    #         self.available_copies += 1
    #         return True
    #     return False
    
    @abstractclassmethod
    def get_item_info(self) -> str:
        pass

    @abstractclassmethod
    def get_item_type(self) -> str:
        pass

# -------------------------------
# Book Class (inherits LibraryItem)
# -------------------------------

class Book(LibraryItem):
    def __init__(self, title: str, author: str, copies: int, isbn: str, num_pages: int): 
        """
        Creates a book in the database immediately.
        """
    
        # Initialize parent with the db ID
        super().__init__(title, author, copies)

        # Store book-specific attributes
        self.author = author
        self.isbn = isbn
        self.num_pages = num_pages

        # Create in db
        book_model = self.db.add_book(title, author, copies, isbn, num_pages)

        # Set database generated ID
        self.id = book_model.id

    def __repr__(self):
        return f"Book(id={self.id}, title='{self.title}', author='{self.author}')"

    def get_item_type(self) -> str:
        return 'Book'
    
    def get_item_info(self) -> str:
        item = self.db.get_item_by_id(self.id)
        return (f"Title: {self.title}\n"
                f"Author: {self.author}\n"
                f"ISBN: {self.isbn}\n"
                f"Pages: {self.num_pages}\n"
                f"Type: {self.get_item_type()}\n"
                f"Available: {item.available_copies}/{item.total_copies}\n"
                f"Can be borrowed: {self.is_available()}")
    

# -------------------------------
# DVD Class (inherits LibraryItem)
# -------------------------------
class DVD(LibraryItem):
    def __init__(self, title: str, director: str, copies: int, duration_minutes: int, genre: str):
        """
        Creates a dvd in the database immediately.
        """
        super().__init__(title, director, copies)
        self.director = director
        self.duration_minutes = duration_minutes
        self.genre = genre

        dvd_model = self.db.add_dvd(title, director, copies, duration_minutes, genre)
        self.id = dvd_model.id
    
    def __repr__(self):
        return f"DVD(id={self.id}, title='{self.title}', director='{self.director}')"

    def get_item_type(self) -> str:
        return 'DVD'
    
    def get_item_info(self) -> str:
        item = self.db.get_item_by_id(self.id)
        return (f"Title: {self.title}\n"
                f"Director: {self.director}\n"
                f"Duration: {self.duration_minutes} minutes\n"
                f"Genre: {self.genre}\n"
                f"Type: {self.get_item_type()}\n"
                f"Available: {item.available_copies}/{item.total_copies}\n"
                f"Can be borrowed: {self.is_available()}")
    
# -------------------------------
# Member Base Class (Observer)
# -------------------------------
class Member(ABC):
    def __init__(self, name: str, email: str, membership_type: str, borrow_limit: int, expiry_date: Optional[date] = None):
        self.name = name
        self.email = email

        self.db = DatabaseManager()

        # create member and membership in db
        member_model = self.db.add_member(name, email, membership_type, borrow_limit, expiry_date)
        self.member_id = member_model.id

        # these are removed:
        # self.borrowed_items: List[int] = []
        # self.notifications: List[str] = []

    def __str__(self) -> str:
        return f'{self.name} ({self.member_id})'
    
    @abstractclassmethod
    def __repr__(self):
        pass
    
    @abstractclassmethod
    def get_max_borrow_limit(self) -> int:
        pass

    def get_borrowed_count(self) -> int:
        """Get count of currently borrowed items of this member from database"""
        borrowed_items = self.db.get_member_borrowed_items(self.member_id)
        return len(borrowed_items)

    def can_borrow(self) -> bool:
        """
        Check if member can borrow more items.
        Checks both borrow limit and membership expiry.
        """
        if self.db.check_membership_expiry(self.member_id):
            return False
        return self.get_borrowed_count() < self.get_max_borrow_limit()
    
    def borrow_item(self, item_id: int) -> bool:
        """
        For compatibility with original interface.
        Returns True if member CAN borrow (doesn't actually borrow).
        Actual borrowing is done through Library class.
        """
        if self.can_borrow():
            # self.borrowed_items.append(item_id)
            return True
        return False

    def return_item(self, item_id: int) -> bool:
        """
        For compatibility with original interface.
        Returns True if member HAS borrowed this item.
        Actual returning is done through Library class.
        """
        borrowed_items = self.db.get_member_borrowed_items(self.member_id)
        item_ids = [item.id for item in borrowed_items]
        return item_id in item_ids
    
    # observer method
    def update(self, message: str) -> None:
        """
        Notification method: Receive notification and persist to database.
        
        This is called by the Library when items become available.
        The notification is stored in the database for the member to view later.
        """
        self.db.create_notification(self.member_id, message)

    def get_notifications(self) -> List[str]:
        """Get member's notifications from database"""
        notifications = self.db.get_member_notifications(self.member_id, unread_only=False)
        return [nf.message for nf in notifications]
    
    def clear_notifications(self) -> None:
        """Mark all notifications as read"""
        notifications = self.db.get_member_notifications(self.member_id, unread_only=True)
        for nf in notifications:
            self.db.mark_notification_read(nf.id)

    
# -------------------------------
# RegularMember
# -------------------------------
class RegularMember(Member):
    """
    Regular member with 3-item borrow limit.
    No expiry date.
    """
    MAX_BORROW_LIMIT = 3
    
    def __init__(self, name: str, email: str):
        super().__init__(
            name, email, 
            membership_type='regular', 
            borrow_limit = self.MAX_BORROW_LIMIT, 
            expiry_date = None
        )
    def __repr__(self):
        return f"Regular Member(id={self.member_id}, name='{self.name}')"
    
    def get_max_borrow_limit(self) -> int:
        return self.MAX_BORROW_LIMIT
    
# -------------------------------
# PremiumMember
# -------------------------------
class PremiumMember(Member):
    """
    Premium member with 5-item borrow limit and expiry date.
    """
    MAX_BORROW_LIMIT = 5
    
    def __init__(self, name: str, email: str, membership_expiry: Optional[str] = None):
        expiry_date = None
        if membership_expiry:
            if isinstance(membership_expiry, str):
                from datetime import datetime
                expiry_date = datetime.strptime(membership_expiry, '%Y-%m-%d').date()
            else:
                expiry_date = membership_expiry
        
        super().__init__(
            name, email,
            membership_type='premium',
            borrow_limit=self.MAX_BORROW_LIMIT,
            expiry_date=expiry_date
        )
        self.membership_expiry = expiry_date
    
    def __repr__(self):
        return f"Premium Member(id={self.member_id}, name='{self.name}')"
    
    def get_max_borrow_limit(self) -> int:
        return self.MAX_BORROW_LIMIT
    

# -------------------------------
# Library Singleton
# -------------------------------    
class Library:
    """
    Singleton Library class that manages all library operations through database.
    Maintains same interface as original OOP implementation.
    To ensure only one library instance exists.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Library, cls).__new__(cls)
            cls._instance._initialized = False 
        return cls._instance
    
    def __init__(self):
        """Initialize library with database manager"""
        if self._initialized:
            return
        
        self.db = DatabaseManager()
        self._initialized = True

    def __len__(self) -> int:
        """Get total number of items in library"""
        items = self.db.get_all_items()
        return len(items)

    # item management
    def add_item(self, item: LibraryItem) -> bool:
        """
        Add item to library (already persisted in item's __init__).
        For compatibility with original interface.
        """
        # Item is already in database from its constructor
        return True
    
    def remove_item(self, item_id: int) -> bool:
        """Remove item from library database"""
        return self.db.remove_item(item_id)
    
    # member management
    def add_member(self, member: Member) -> bool:
        """
        Add member to library (already persisted in member's __init__).
        For compatibility with original interface.
        """
        # Member is already in database from its constructor
        return True
    
    def remove_member(self, member_id: int) -> bool:
        """Remove member from library database"""
        return self.db.remove_member(member_id)
    
    # borrow and return item
    def borrow_item(self, member_id: int, item_id: int) -> bool:
        """
        Borrow an item from the library.
        Checks availability and borrow limits through database.
        """
        return self.db.borrow_item(member_id, item_id)
    
    def return_item(self, member_id: int, item_id: int) -> bool:
        """
        Return an item to the library.
        Triggers notifications for waiting members.
        """
        success = self.db.return_item(member_id, item_id)

        if success:
            # Notify waiting members
            self.db.notify_waiting_members(item_id)
        
        return success
    
    # search
    def search_items(self, query: str) -> List[LibraryItemModel]:
        """
        Search items by title or creator.
        Returns list of LibraryItemModel objects from database.
        """
        return self.db.search_items(query)
    
    # display
    def display_all_items(self) -> None:
        items = self.db.get_all_items()
        print('All Items in the Library:')
        for item in items:
            print(f'{repr(item)} | Available: {item.available_copies}/{item.total_copies}\n')

    def display_all_members(self) -> None:
        members = self.db.get_all_members()
        print('All Members in the Library')
        for member in members:
            print(repr(member))

    # waiting list / observer
    def get_waiting_list(self, item_id: int) -> List[MemberModel]:
        """Get list of members waiting for an item"""
        return self.db.get_waiting_list(item_id)
    
    def join_waiting_list(self, member_id: int, item_id: int) -> bool:
        """
        Add member to waiting list for an item.
        Only works if item is currently unavailable.
        """
        # Check if item is currently available
        item = self.db.get_item_by_id(item_id)
        if item and item.is_available():
            return False 

        return self.db.join_waiting_list(member_id, item_id)
    
    def leave_waiting_list(self, member_id: int, item_id: int) -> bool:
        return self.db.leave_waiting_list(member_id, item_id)
    
    def notify_waiting_members(self, item_id: int) -> None:
        # Check if item is available
        item = self.db.get_item_by_id(item_id)
        if not item or not item.is_available():
            return

        # Get waiting members from database
        waiting_members = self.db.get_waiting_list(item_id)

        # Notify 
        message = f"'{item.title}' is now available"
        for member in waiting_members:
            self.db.create_notification(member.id, message)

def main():
    print("=" * 70)
    print("LIBRARY MANAGEMENT SYSTEM - DATABASE INTEGRATION DEMO")
    print("=" * 70)
    
    # Initialize database (drop and recreate tables)
    db = DatabaseManager()
    print("\nInitializing database...")
    db.drop_tables()
    db.create_tables()
    print("Database initialized!\n")

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