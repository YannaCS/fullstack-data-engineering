from sqlmodel import create_engine
from sqlmodel import Session

# from sqlalchemy import URL

DATABASE_URL = "postgresql://postgres:mypassword@localhost:5432/postgres"

engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"options": "-csearch_path=note_app"}
)

def get_session():
    with Session(engine) as session:
        yield session

