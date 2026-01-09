# run: python -m app.data_init    
# treats app as a package, so relative imports and module‑level imports inside will resolve properly
from sqlmodel import SQLModel, Session
from app.database import engine
from app.models import User, Note

def create_tables():
    SQLModel.metadata.create_all(engine)
    

if __name__ == '__main__':
    create_tables()

    with Session(engine) as session:
        user = User(
            email='admin@example.com',
            username='admin user',
            hash_password='initialpassword'
        )
        session.add(user)
        session.commit()
        
        print(f'created user {user.id} {user.username}')
        if user.id:
            note = Note(
                title="first note",
                content="Learn Python",
                user_id=user.id
            )
            session.add(note)
            session.commit()
            print(f'session added {note.id}')