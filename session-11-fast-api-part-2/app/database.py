from sqlmodel import create_engine
from sqlmodel import Session

DATABASE_URL = "postgresql://postgres:mypassword@localhost:5432/note-app"

engine = create_engine(
    DATABASE_URL,
    echo=True
)

def get_session():
    with Session(engine) as session:
        yield session

