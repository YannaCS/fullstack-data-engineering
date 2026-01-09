from sqlmodel import create_engine, Session

DATABASE_URL = "postgresql://postgres:mypassword@localhost:5432/postgres"
engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"options": "-csearch_path=weather_forecast"}
)

def get_session():
    with Session(engine) as session:
        yield session