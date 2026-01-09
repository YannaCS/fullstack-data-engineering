from sqlalchemy import create_engine, text   # Creates connection to database
from sqlalchemy.orm import sessionmaker, Session   # Manages database sessions
from contextlib import contextmanager   # For creating context managers (with statements)
# Import all SQLAlchemy models from models.py
from models import (
    Base,   # Base class for all models
    LibraryItemModel, 
    BookModel, 
    DVDModel, 
    MemberModel, 
    MembershipModel, 
    BorrowedItemModel, 
    WaitingListModel, 
    NotificationModel
)
from typing import List, Optional  # type hints for better code documentation
from datetime import datetime, date

class DatabaseManager:
    """
    Singleton class that manages all database operations.
    Only one instance exists throughout the application.
    """
    _instance = None

    def __new__(cls):
        """
        Controls object creation to implement Singleton pattern.
        This runs BEFORE __init__
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Add flag to track if __init__ has run
            cls._instance._initialized = False
        
        return cls._instance
    
    def __init__(self):
        """
        Initialize database connection.
        Only runs once due to _initialized flag.
        """
        # Skip if already initialized (Singleton pattern)
        if self._initialized:
            return 
        
        # database connection string
        DATABASE_URL = "postgresql://postgres:mypassword@localhost:5432/postgres"

        # engine = connection pool to database
        # echo=True prints all SQL statements (useful for debugging)
        self.engine = create_engine(DATABASE_URL, echo=False)
        
        # session factory
        # session refers to an object that allows for the persistence of data or parameters across multiple interactions or requests
        # sessionmaker = factory that creates Session objects
        # bind=self.engine connects sessions to our database
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # Mark as initialized so __init__ doesn't run again
        self._initialized = True

    # context manager provides a neat way to automatically set up and clean up resources
    @contextmanager
    def get_session(self):
        """
        Context manager for database sessions.
        Automatically handles commit/rollback/close.
        
        Usage:
            with db.get_session() as session:
                session.query(...)
        """
        # Create a new session
        session = self.SessionLocal()

        try:
            # yield = pause here and give session to caller
            # Code inside 'with' block runs here
            yield session
            # After 'with' block, commit changes to database
            session.commit()

        except Exception as e:
            # If any error occurs, undo all changes
            session.rollback()
            raise e
        
        finally:
            # Always close session, even if error occurred
            # Releases database connection back to pool
            session.close()

    def create_tables(self):
        """
        Create all tables defined in models.py
        Safe to call multiple times (won't recreate existing tables)
        """
        Base.metadata.create_all(self.engine)
    
    def drop_tables(self):
        """
        Drop all tables from database.
        WARNING: Deletes all data! Use only for testing.
        Uses CASCADE to handle circular dependencies.
        """
        with self.engine.begin() as conn:
            conn.execute(text("DROP SCHEMA IF EXISTS librarymgtsys CASCADE"))
            conn.execute(text("CREATE SCHEMA librarymgtsys"))

    # ========================
    # ITEM OPERATIONS
    # ========================
    def add_book(self, title: str, author: str, copies: int, isbn: str, num_pages: int) -> BookModel:
        """
        Add a new book to the database.
        Creates both LibraryItemModel and BookModel records.
        """
        # Use context manager for automatic session handling
        with self.get_session() as session:
            # 1. Create library_items record
            library_item = LibraryItemModel(
                title = title,
                creator = author,
                item_type = 'book',
                total_copies = copies,
                available_copies = copies
            )

            # Add to session (staged, not committed yet)
            session.add(library_item)

            # flush() = Send to database to get auto-generated ID
            # But not commit transaction yet
            session.flush()

            # 2. create books record using the id from library_items
            book = BookModel(
                id = library_item.id,
                isbn = isbn,
                num_pages = num_pages
            )

            # add book to session
            session.add(book)
            session.flush()
            session.expunge(book)
            # Commit happens automatically when exiting 'with' block
            # Both records are saved together (transaction)

            return book
    
    def add_dvd(self, title: str, director: str, copies: int, duration_minutes: int, genre: str) -> DVDModel:
        """
        Add a new DVD to the database.
        Creates both LibraryItemModel and DVDModel records.
        Similar as above add_book
        """
        with self.get_session() as session:
            library_item = LibraryItemModel(
                title = title,
                creator = director,
                item_type = 'dvd',
                total_copies = copies,
                available_copies = copies
            )

            session.add(library_item)
            session.flush()

            dvd = DVDModel(
                id = library_item.id,
                duration_minutes = duration_minutes,
                genre = genre
            )

            session.add(dvd)
            session.flush()
            session.expunge(dvd)
            return dvd
        
    def remove_item(self, item_id: int) -> bool:
        """
        Remove an item from database.
        CASCADE will automatically delete related books/dvds/borrowed_items.
        """
        with self.get_session() as session:
            # query the item by id
            item = session.query(LibraryItemModel).filter(LibraryItemModel.id == item_id).first()

            # Check if item exists
            if item:
                session.delete(item) # Delete from database
                # Commit happens automatically
                return True
            
            return False
        
    def get_item_by_id(self, item_id: int) -> Optional[LibraryItemModel]:
        """
        Retrieve a single item by its ID.
        Returns None if not found.
        """
        with self.get_session() as session:
            # .get() is shorthand for querying by primary key
            item = session.query(LibraryItemModel).get(item_id)

            # Important: Detach from session before returning
            # Otherwise accessing attributes outside session fails
            if item:
                session.expunge(item) # Detach from session
            
            return item
        
    def search_items(self, query: str) -> List[LibraryItemModel]:
        """
        Search items by title or creator (case-insensitive).
        Returns list of matching items.
        """
        with self.get_session() as session:
            query_lower = query.lower()

            # SQLAlchemy query:
            # .filter() = WHERE clause
            # .ilike() = case-insensitive LIKE (SQL: ILIKE)
            # % = wildcard (matches anything)
            items = session.query(LibraryItemModel).filter(
                (LibraryItemModel.title.ilike(f'%{query_lower}%')) |
                (LibraryItemModel.creator.ilike(f'%{query_lower}%'))
            ).all()

            # Detach all items from session
            for item in items:
                session.expunge(item)

            return items
        
    def get_all_items(self) -> List[LibraryItemModel]:
        """
        Get all items in the library.
        """
        with self.get_session() as session:
            items = session.query(LibraryItemModel).all()

            for item in items:
                session.expunge(item)

            return items
        
    # ========================
    # MEMBER OPERATIONS
    # ========================
    def add_member(self, name: str, email: str, membership_type: str, borrow_limit: int, expiry_date: Optional[date] = None) -> MemberModel:
        """
        Add a new member with membership.
        Creates both MemberModel and MembershipModel (circular FK relationship).
        """
        with self.get_session() as session:
            # to deal with circular reference between  member and membership and not null for both side
            session.execute(text("SET CONSTRAINTS ALL DEFERRED"))

            # 1. Create membership record first (without member_id)
            membership = MembershipModel(
                member_id = None, # temporary, will update after creating member
                membership_type = membership_type,
                borrow_limit = borrow_limit,
                expiry_date = expiry_date
            )
            session.add(membership)
            session.flush()  # get membership_id

            # 2. Create member
            member = MemberModel(
                name = name,
                email = email,
                membership_id = membership.id
            )
            session.add(member)
            session.flush() # get member_id

            # 3. Upadte member_id in membership
            membership.member_id = member.id
            session.flush()
            session.expunge(member)
            # Commit both together
            # Constraints checked here at commit time
            return member
        
    def remove_member(self, member_id: int) -> bool:
        """
        Remove a member from database.
        CASCADE deletes related borrowed_items, notifications, etc.
        """
        with self.get_session() as session:
            member = session.query(MemberModel).filter(MemberModel.id == member_id).first()

            if member:
                session.delete(member)
                return True

            return False
        
    def get_member_by_id(self, member_id: int) -> Optional[MemberModel]:
        """
        Get a member by ID.
        """
        with self.get_session() as session:
            member = session.query(MemberModel).get(member_id)

            if member:
                session.expunge(member)
            
            return member
    
    def get_all_members(self) -> List[MemberModel]:
        """
        Get a list of all members.
        """
        with self.get_session() as session:
            members = session.query(MemberModel).all()
            for member in members:
                session.expunge(member)
            
            return members
        
    # ========================
    # MEMBERSHIP OPERATIONS
    # ========================
    def get_membership(self, member_id: int) -> Optional[MembershipModel]:
        """
        Get membership details for a member by member's ID.
        """
        with self.get_session() as session:
            # Query by member_id (not primary key)
            membership = session.query(MembershipModel).filter(
                MembershipModel.member_id == member_id
            ).first()

            if membership:
                session.expunge(membership)
            
            return membership
        
    def update_membership(self, member_id: int, membership_type: Optional[str] = None, 
                         borrow_limit: Optional[int] = None, expiry_date: Optional[date] = None) -> bool:
        """
        Update membership details.
        Only updates fields that are provided (not None).
        """
        with self.get_session() as session:
            membership = session.query(MembershipModel).filter(
                MembershipModel.member_id == member_id
            ).first()

            if not membership:
                return False
            
            if membership_type is not None:
                membership.membership_type = membership_type
            
            if borrow_limit is not None:
                membership.borrow_limit = borrow_limit
            
            if expiry_date is not None:
                membership.expiry_date = expiry_date

            membership.updated_at = datetime.now()

            return True
        
    def renew_membership(self, member_id: int, days: int) -> bool:
        """
        Renew membership by extending expiry date.
        """
        with self.get_session() as session:
            membership = session.query(MembershipModel).filter(
                MembershipModel.member_id == member_id
            ).first()

            if not membership:
                return False
            
            # Use the model's renew method directly
            membership.renew(days)

            return True
    
    def check_membership_expiry(self, member_id: int) -> bool:
        """
        Check if a member's membership is expired.
        Returns True if expired, False otherwise.
        """
        with self.get_session() as session:
            membership = session.query(MembershipModel).filter(
                MembershipModel.member_id == member_id
            ).first()

            if not membership:
                return False
            
            return membership.is_expired()

    # ========================
    # BORROWING OPERATIONS
    # ========================
    def borrow_item(self, member_id: int, item_id: int) -> bool:
        """
        Record a borrow transaction.
        Decreases available_copies.
        
        Returns True if successful, False otherwise.
        """
        with self.get_session() as session:
            member = session.query(MemberModel).get(member_id)
            item = session.query(LibraryItemModel).get(item_id)

            if not member or not item:
                return False
            
            if not item.is_available():
                return False
            
            if not member.can_borrow():
                return False
            
            # Otherwise, it can be borrowed
            # Create borrowed record
            borrowed_item = BorrowedItemModel(
                member_id = member_id,
                item_id = item_id,
                status = 'borrowed'
            )
            session.add(borrowed_item)
            # Update available copies
            item.available_copies -= 1

            # Commit both changes together (transaction)
            return True
        
    def return_item(self, member_id: int, item_id: int) -> bool:
        """
        Record a return transaction.
        Increases available_copies.
        Marks borrow record as 'returned'.
        """
        with self.get_session() as session:
            # Find the active borrow record
            borrowed_item = session.query(BorrowedItemModel).filter(
                BorrowedItemModel.member_id == member_id,
                BorrowedItemModel.item_id == item_id,
                BorrowedItemModel.status == 'borrowed'
            ).first()

            if not borrowed_item:
                return False
            
            item = session.query(LibraryItemModel).get(item_id)
            if not item:
                return False
            
            # Update borrowed record
            borrowed_item.status = 'returned'
            borrowed_item.return_date = datetime.now()

            # Update item's available copies
            item.available_copies += 1

            # Commit changes
            return True
        
    def get_member_borrowed_items(self, member_id: int) -> List[LibraryItemModel]:
        """
        Get all items currently borrowed by a member.
        """
        with self.get_session() as session:
            # Join borrowed_items with library_items
            items = session.query(LibraryItemModel).join(
                BorrowedItemModel,
                LibraryItemModel.id == BorrowedItemModel.item_id
            ).filter(
                BorrowedItemModel.member_id == member_id,
                BorrowedItemModel.status == 'borrowed'
            ).all()

            for item in items:
                session.expunge(item)

            return items
        
    def get_item_borrow_history(self, item_id: int) -> List[BorrowedItemModel]:
        """
        Get complete borrow history for an item.
        """
        with self.get_session() as session:
            history = session.query(BorrowedItemModel).filter(
                BorrowedItemModel.item_id == item_id
            ).order_by(BorrowedItemModel.borrow_date.desc()).all()

            for h in history:
                session.expunge(h)

            return history
        
    # ========================
    # WAITING LIST OPERATIONS
    # ========================
    def join_waiting_list(self, member_id: int, item_id: int) -> bool:
        """
        Add member to waiting list for an item.
        Prevents duplicates with UNIQUE constraint.
        """
        with self.get_session() as session:
            try:
                # check if already in waiting list
                existing = session.query(WaitingListModel).filter(
                    WaitingListModel.member_id == member_id,
                    WaitingListModel.item_id == item_id
                ).first()

                if existing:
                    return False
                
                # else, add to waiting list
                waiting = WaitingListModel(
                    member_id = member_id,
                    item_id = item_id
                )

                session.add(waiting)
                return True
            
            except Exception:
                # UNIQUE constraint violation or other error
                return False
            
    def leave_waiting_list(self, member_id: int, item_id: int) -> bool:
        """
        Remove member from waiting list.
        """
        with self.get_session() as session:
            waiting = session.query(WaitingListModel).filter(
                WaitingListModel.member_id == member_id,
                WaitingListModel.item_id == item_id
            ).first()

            if waiting:
                session.delete(waiting)
                return True
            
            return False
    
    def get_waiting_list(self, item_id: int) -> List[MemberModel]:
        """
        Get all members waiting for an item (ordered by join time).
        """
        with self.get_session() as session:
            # Join waiting_list with members
            members = session.query(MemberModel).join(
                WaitingListModel,
                MemberModel.id == WaitingListModel.member_id
            ).filter(
                WaitingListModel.item_id == item_id
            ).order_by(WaitingListModel.joined_at).all()

            for member in members:
                session.expunge(member)

            return members
        
    def notify_waiting_members(self, item_id: int) -> bool:
        """
        Create notifications for all members waiting for an item.
        """
        with self.get_session() as session:
            # Check if item exist
            # item title for notification message
            item = session.query(LibraryItemModel).get(item_id)
            if not item:
                return False
            
            # Get waiting records with member id
            waitings = session.query(WaitingListModel).filter(
                WaitingListModel.item_id == item_id
            ).all()

            # Create notification for each member
            for record in waitings:
                notification = NotificationModel(
                    member_id = record.member_id,
                    message = f"'{item.title}' is now available"
                )
                session.add(notification)

            # Commit all notifications
            return True
    # ========================
    # NOTIFICATION OPERATIONS
    # ========================
    def create_notification(self, member_id: int, message: str) -> NotificationModel:
        """
        Create a notification for a member.
        """
        with self.get_session() as session:
            notification = NotificationModel(
                member_id = member_id,
                message = message,
                is_read = False
            )

            session.add(notification)

            return notification
        
    def get_member_notifications(self, member_id: int, unread_only: bool = False) -> List[NotificationModel]:
        """
        Get notifications for a member.
        Can filter to only unread notifications.
        """
        with self.get_session() as session:
            nfs = session.query(NotificationModel).filter(
                NotificationModel.member_id == member_id
            )

            if unread_only:
                nfs = nfs.filter(
                    NotificationModel.is_read == False
                )
            
            nfs = nfs.order_by(NotificationModel.created_at.desc()).all()

            for nf in nfs:
                session.expunge(nf)

            return nfs
        
    def mark_notification_read(self, notification_id: int) -> bool:
        """
        Mark a notification as read.
        """
        with self.get_session() as session:
            nf = session.query(NotificationModel).get(notification_id)

            if nf:
                nf.is_read = True
                return True
            
            return False
