from sqlalchemy import create_engine

DATABASE_URL = "postgresql://postgres:mypassword@localhost:5432/postgres"

engine = create_engine(
    DATABASE_URL,
    echo=True
)

