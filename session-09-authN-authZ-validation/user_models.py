from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from db import db

# User model (main table)
class User(db.Model):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    role = Column(String(50), nullable=False, default='user')  # Add role column
    
    # One-to-one relationship to Password
    password = relationship('Password', 
                           uselist=False, 
                           back_populates='user',
                           cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', role='{self.role}')>"

# Password model (1-to-1 with User)
class Password(db.Model):
    __tablename__ = 'passwords'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Relationship back to User
    user = relationship('User', back_populates='password')
    
    def __repr__(self):
        return f"<Password(user_id={self.user_id})>"

# only for development purposes
if __name__ == '__main__':
    from create_app import create_app
    app = create_app()
    with app.app_context():
        db.create_all()




