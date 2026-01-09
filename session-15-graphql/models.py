
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, Session, relationship
from datetime import datetime
from engine import async_session_local, engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

# ============ DATABASE SETUP ============

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    posts = relationship("Post", back_populates="author")

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    author = relationship("User", back_populates="posts")

if __name__ == "__main__":
    Base.metadata.create_all(engine)

    # Seed data for 3 users and 10 posts
    with Session(engine) as session:
        # Create sample users
        user1 = User(name="Alice Smith", email="alice@example.com")
        user2 = User(name="Bob Johnson", email="bob@example.com")
        user3 = User(name="Charlie Brown", email="charlie@example.com")

        # Create sample posts (assign in a round-robin fashion)
        posts = [
            Post(title="Hello World", content="This is my first post!", author=user1),
            Post(title="GraphQL is great", content="Let's learn GraphQL together.", author=user1),
            Post(title="Alice's Adventures", content="Today I went to the library.", author=user1),
            Post(title="Bob's Thoughts", content="Here's what I think about REST.", author=user2),
            Post(title="REST vs GraphQL", content="Comparing API paradigms.", author=user2),
            Post(title="My Weekend", content="I went hiking with friends.", author=user2),
            Post(title="Charlie's Chatter", content="I'm excited to share my ideas here.", author=user3),
            Post(title="Tips & Tricks", content="How to debug Python code.", author=user3),
            Post(title="The Power of SQL", content="Queries that changed my project.", author=user3),
            Post(title="Favorite Libraries", content="Some Python libraries I love.", author=user3)
        ]

        # Add users and posts to session
        session.add_all([user1, user2, user3])
        session.add_all(posts)
        session.commit()

        print("Seed data inserted")