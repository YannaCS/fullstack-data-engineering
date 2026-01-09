from sqlalchemy import (
    Column, Integer, String, DateTime, Date, Boolean, Text,
    ForeignKey, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import relationship, DeclarativeBase # declarative_base # this is old version
from sqlalchemy.sql import func
from datetime import datetime, date
from typing import List, Optional

# Base = declarative_base()
class Base(DeclarativeBase):
    pass


class LibraryItemModel(Base):
    __tablename__ = 'library_items'
    __table_args__ = {'schema': 'librarymgtsys'}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    creator = Column(String(255), nullable=False)
    item_type = Column(String(20), nullable=False)
    total_copies = Column(Integer, nullable=False, default=1)
    available_copies = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, default=func.current_timestamp())
    
    # Relationships
    book = relationship("BookModel", back_populates="library_item", uselist=False, cascade="all, delete-orphan")
    dvd = relationship("DVDModel", back_populates="library_item", uselist=False, cascade="all, delete-orphan")
    borrowed_items = relationship("BorrowedItemModel", back_populates="library_item", cascade="all, delete-orphan")
    waiting_list_entries = relationship("WaitingListModel", back_populates="library_item", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint("item_type IN ('book', 'dvd')", name='check_item_type'),
        CheckConstraint('available_copies <= total_copies', name='check_copies'),
        {'schema': 'librarymgtsys'}
    )
    
    def is_available(self) -> bool:
        """check if item is available for borrowing"""
        return self.available_copies > 0
    
    def get_active_borrows(self) -> List['BorrowedItemModel']:
        """get all active, not returned, borrows for this item"""
        return [borrow for borrow in self.borrowed_items if borrow.status == 'borrowed']
    
    def __repr__(self):
        return f"<LibraryItem(id={self.id}, title='{self.title}', type='{self.item_type}', available={self.available_copies}/{self.total_copies})>"


class BookModel(Base):
    __tablename__ = 'books'
    __table_args__ = {'schema': 'librarymgtsys'}
    
    id = Column(Integer, ForeignKey('librarymgtsys.library_items.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    isbn = Column(String(20), nullable=False, unique=True)
    num_pages = Column(Integer, nullable=False)
    
    # Relationships
    library_item = relationship("LibraryItemModel", back_populates="book")
    
    def __repr__(self):
        return f"<Book(id={self.id}, isbn='{self.isbn}', pages={self.num_pages})>"


class DVDModel(Base):
    __tablename__ = 'dvds'
    __table_args__ = {'schema': 'librarymgtsys'}
    
    id = Column(Integer, ForeignKey('librarymgtsys.library_items.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    duration_minutes = Column(Integer, nullable=False)
    genre = Column(String(50), nullable=False)
    
    # Relationships
    library_item = relationship("LibraryItemModel", back_populates="dvd")
    
    def __repr__(self):
        return f"<DVD(id={self.id}, duration={self.duration_minutes}min, genre='{self.genre}')>"


class MembershipModel(Base):
    __tablename__ = 'memberships'
    __table_args__ = {'schema': 'librarymgtsys'}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey('librarymgtsys.members.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=True, unique=True)
    membership_type = Column(String(20), nullable=False)
    borrow_limit = Column(Integer, nullable=False)
    expiry_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    # REMOVE back_populates temporarily
    # We'll add it back in MemberModel
    # member = relationship("MemberModel", back_populates="membership", foreign_keys=[member_id])
    
    __table_args__ = (
        CheckConstraint("membership_type IN ('regular', 'premium')", name='check_membership_type'),
        CheckConstraint(
            "(membership_type = 'regular' AND expiry_date IS NULL) OR (membership_type = 'premium' AND expiry_date IS NOT NULL)",
            name='check_expiry_date'
        ),
        {'schema': 'librarymgtsys'}
    )
    
    def is_expired(self) -> bool:
        """check if premium membership is expired"""
        if self.membership_type == 'regular':
            return False
        if self.expiry_date is None:
            return False
        return date.today() > self.expiry_date
    
    def days_until_expiry(self) -> int:
        """get days until expiry. Returns -1 for regular or expired memberships"""
        if self.membership_type == 'regular' or self.expiry_date is None:
            return -1
        delta = self.expiry_date - date.today()
        return max(0, delta.days)
    
    def renew(self, days: int) -> None:
        """renew membership by extending expiry date"""
        if self.membership_type == 'premium' and self.expiry_date:
            from datetime import timedelta
            # if already expired, renew from today, otherwise extend current expiry
            if self.is_expired():
                self.expiry_date = date.today() + timedelta(days=days)
            else:
                self.expiry_date = self.expiry_date + timedelta(days=days)
            self.updated_at = datetime.now()
    
    def __repr__(self):
        expiry_str = f", expires={self.expiry_date}" if self.expiry_date else ""
        return f"<Membership(id={self.id}, type='{self.membership_type}', limit={self.borrow_limit}{expiry_str})>"


class MemberModel(Base):
    __tablename__ = 'members'
    __table_args__ = {'schema': 'librarymgtsys'}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    membership_id = Column(Integer, ForeignKey('librarymgtsys.memberships.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    
    # Relationships
    membership = relationship(
        "MembershipModel", 
        foreign_keys=[membership_id],
        uselist=False, # makes it one-to-one instead of one-to-many
        backref="member" # creates the reverse relationship automatically
    )
    borrowed_items = relationship("BorrowedItemModel", back_populates="member", cascade="all, delete-orphan")
    waiting_list_entries = relationship("WaitingListModel", back_populates="member", cascade="all, delete-orphan")
    notifications = relationship("NotificationModel", back_populates="member", cascade="all, delete-orphan")
    
    def get_borrowed_count(self) -> int:
        """get count of currently borrowed (not returned) items"""
        return len([borrow for borrow in self.borrowed_items if borrow.status == 'borrowed'])
    
    def can_borrow(self) -> bool:
        """check if member can borrow more items"""
        if self.membership and self.membership.is_expired():
            return False
        return self.get_borrowed_count() < self.get_borrow_limit()
    
    def get_borrow_limit(self) -> int:
        """get member's borrow limit from membership"""
        if self.membership:
            return self.membership.borrow_limit
        return 0
    
    def __repr__(self):
        return f"<Member(id={self.id}, name='{self.name}', email='{self.email}')>"


class BorrowedItemModel(Base):
    __tablename__ = 'borrowed_items'
    __table_args__ = {'schema': 'librarymgtsys'}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey('librarymgtsys.members.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    item_id = Column(Integer, ForeignKey('librarymgtsys.library_items.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    borrow_date = Column(DateTime, default=func.current_timestamp())
    return_date = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=False, default='borrowed')
    
    # Relationships
    member = relationship("MemberModel", back_populates="borrowed_items")
    library_item = relationship("LibraryItemModel", back_populates="borrowed_items")
    
    __table_args__ = (
        CheckConstraint("status IN ('borrowed', 'returned')", name='check_status'),
        {'schema': 'librarymgtsys'}
    )
    
    def __repr__(self):
        return f"<BorrowedItem(id={self.id}, member_id={self.member_id}, item_id={self.item_id}, status='{self.status}')>"


class WaitingListModel(Base):
    __tablename__ = 'waiting_list'
    __table_args__ = {'schema': 'librarymgtsys'}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey('librarymgtsys.members.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    item_id = Column(Integer, ForeignKey('librarymgtsys.library_items.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    joined_at = Column(DateTime, default=func.current_timestamp())
    
    # Relationships
    member = relationship("MemberModel", back_populates="waiting_list_entries")
    library_item = relationship("LibraryItemModel", back_populates="waiting_list_entries")
    
    __table_args__ = (
        UniqueConstraint('member_id', 'item_id', name='unique_member_item'),
        {'schema': 'librarymgtsys'}
    )
    
    def __repr__(self):
        return f"<WaitingList(id={self.id}, member_id={self.member_id}, item_id={self.item_id})>"


class NotificationModel(Base):
    __tablename__ = 'notifications'
    __table_args__ = {'schema': 'librarymgtsys'}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey('librarymgtsys.members.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    
    # Relationships
    member = relationship("MemberModel", back_populates="notifications")
    
    def __repr__(self):
        return f"<Notification(id={self.id}, member_id={self.member_id}, read={self.is_read})>"