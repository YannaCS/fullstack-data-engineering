from abc import ABC, abstractclassmethod
from typing import List, Dict

# -------------------------------
# LibraryItem (Abstract Base Class)
# -------------------------------
class LibraryItem(ABC):
    _id_counter = 1

    def __init__(self, title: str, creator: str, total_copies: int, ):
        self.id = LibraryItem._id_counter 
        LibraryItem._id_counter += 1

        self.title = title
        self.creator = creator
        self.total_copies = total_copies
        self.available_copies = total_copies

    def __str__(self) -> str:
        return f'{self.title} by {self.creator}'
    
    def __eq__(self, other) -> bool:
        if isinstance(other, LibraryItem):
            return self.id == other.id
        return False

    def is_available(self) -> bool:
        return self.available_copies > 0
    
    def borrow(self) -> bool:
        if self.is_available():
            self.available_copies -= 1
            return True
        return False
    
    def return_item(self) -> bool:
        if self.available_copies < self.total_copies:
            self.available_copies += 1
            return True
        return False
    
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
        super().__init__(title, author, copies)
        self.author = author
        self.isbn = isbn
        self.num_pages = num_pages

    def get_item_type(self) -> str:
        return 'Book'
    
    def get_item_info(self) -> str:
        return (f"Title: {self.title}\n"
                f"Author: {self.author}\n"
                f"ISBN: {self.isbn}\n"
                f"Pages: {self.num_pages}\n"
                f"Type: {self.get_item_type()}"
                f"Can be borrowed: {self.is_available()}")
    

# -------------------------------
# DVD Class (inherits LibraryItem)
# -------------------------------
class DVD(LibraryItem):
    def __init__(self, title: str, director: str, copies: int, duration_minutes: int, genre: str):
        super().__init__(title, director, copies)
        self.director = director
        self.duration_minutes = duration_minutes
        self.genre = genre

    def get_item_type(self) -> str:
        return 'DVD'
    
    def get_item_info(self) -> str:
        return (f"Title: {self.title}\n"
                f"Director: {self.director}\n"
                f"Duration: {self.duration_minutes} minutes\n"
                f"Genre: {self.genre}\n"
                f"Type: {self.get_item_type()}"
                f"Can be borrowed: {self.is_available()}")
    
# -------------------------------
# Member Base Class (Observer)
# -------------------------------
class Member(ABC):
    _id_counter = 1

    def __init__(self, name: str, email: str):
        self.member_id = Member._id_counter
        Member._id_counter += 1

        self.name = name
        self.email = email
        self.borrowed_items: List[int] = []
        self.notifications: List[str] = []

    def __str__(self) -> str:
        return f'{self.name} ({self.member_id})'
    
    @abstractclassmethod
    def get_max_borrow_limit(self) -> int:
        pass

    def can_borrow(self) -> bool:
        return len(self.borrowed_items) < self.get_max_borrow_limit()
    
    def borrow_item(self, item_id: int) -> bool:
        # library part will be done in Library
        if self.can_borrow():
            self.borrowed_items.append(item_id)
            return True
        return False

    def return_item(self, item_id: int) -> bool:
        if item_id in self.borrowed_items:
            self.borrowed_items.remove(item_id)
            return True
        return False
    
    def get_borrowed_count(self) -> int:
        return len(self.borrowed_items)
    
    # observer method
    def update(self, message: str) -> None:
        self.notifications.append(message)

    def get_notifications(self) -> List[str]:
        return self.notifications.copy()
    
    def clear_notifications(self) -> None:
        self.notifications.clear()

    
# -------------------------------
# RegularMember
# -------------------------------
class RegularMember(Member):
    MAX_BORROW_LIMIT: int = 3

    def get_max_borrow_limit(self) -> int:
        return self.MAX_BORROW_LIMIT
    
# -------------------------------
# PremiumMember
# -------------------------------
class PremiumMember(Member):
    MAX_BORROW_LIMIT: int = 5
    def __init__(self, name: str, email: str, membership_expiry=None):
        super().__init__(name, email)
        self.membership_expiry = membership_expiry
    
    def get_max_borrow_limit(self) -> int:
        return self.MAX_BORROW_LIMIT
    

# -------------------------------
# Library Singleton
# -------------------------------    
class Library:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Library, cls).__new__(cls)
            cls._instance.items = {}
            cls._instance.members = {}
            cls._instance.waiting_list = {}
        
        return cls._instance
    
    def __len__(self) -> int:
        return len(self.items)

    # item management
    def add_item(self, item: LibraryItem) -> bool:
        self.items[item.id] = item
        return True
    
    def remove_item(self, item_id: int) -> bool:
        if item_id in self.items:
            del self.items[item_id]
            self.waiting_list.pop(item_id, None)
            return True
        return False
    
    # member management
    def add_member(self, member: Member) -> bool:
        self.members[member.member_id] = member
        return True
    
    def remove_member(self, member_id: int) -> bool:
        if member_id in self.members:
            del self.members[member_id]
            for waiting in self.waiting_list.values():
                waiting[:] = [m for m in waiting if m.member_id != member_id ]
            return True
        return False
    
    # borrow and return item
    def borrow_item(self, member_id: int, item_id: int) -> bool:
        member = self.members.get(member_id)
        item = self.items.get(item_id)
        if member and item and item.is_available() and member.can_borrow():
            if item.borrow():
                member.borrow_item(item_id)
                return True
        return False
    
    def return_item(self, member_id: int, item_id: int) -> bool:
        member = self.members.get(member_id)
        item = self.items.get(item_id)

        if member and item:
            if member.return_item(item_id):
                item.return_item()
                self.notify_waiting_members(item_id)
                return True
        return False
    
    # search
    def search_items(self, query: str) -> List[LibraryItem]:
        query_lower = query.lower()
        return [
            item for item in self.items.values() 
            if query_lower in item.title.lower() or query_lower in item.creator.lower()
            ]
    
    # display
    def display_all_items(self) -> None:
        for item in self.items.values():
            print(f'{item.id}: {item.get_item_info()}\n')

    def display_all_members(self) -> None:
        for member in self.members.values():
            print('All members:') 
            print(f"{member}\n")

    # waiting list / observer
    def get_waiting_list(self, item_id: int) -> List[Member]:
        return self.waiting_list.get(item_id, [])
    
    def join_waiting_list(self, member_id: int, item_id: int) -> bool:
        member = self.members.get(member_id)
        item = self.items.get(item_id)

        # Only join if the item is currently unavailable
        if item.is_available():
            return False
        if member and item:
            # Add member if not already in the waiting list
            if self.get_waiting_list(item_id) and member not in self.get_waiting_list[item_id]:
                self.waiting_list[item_id].append(member)
                return True
        return False
    
    def leave_waiting_list(self, member_id: int, item_id: int) -> bool:
        member = self.members.get(member_id)
        if self.get_waiting_list(item_id) and member in self.get_waiting_list[item_id]:
            self.waiting_list[item_id] = [m for m in self.waiting_list[item_id] if m.member_id != member_id]
            return True
        return False
    
    def notify_waiting_members(self, item_id: int) -> None:
        item = self.items.get(item_id)
        if item and item.is_available():
            waiting_members = self.get_waiting_list(item_id)
            for m in waiting_members:
                m.update(f'<{item.title}> is now available')
    

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