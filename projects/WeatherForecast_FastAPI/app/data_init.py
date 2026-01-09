from sqlmodel import SQLModel, Session
from app.database import engine
from app.models import User, Task

def create_tables():
    SQLModel.metadata.create_all(engine)

if __name__ == '__main__':
    create_tables()

    with Session(engine) as session:
        user = User(
            name = 'John'
        )
        session.add(user)
        session.commit()

        print(f'created user {user.id} {user.name}')
        if user.id:
            task = Task(
                title = "test task",
                content="search weather in Seattle",
                city='Seattle',
                user_id=user.id
            )

            session.add(task)
            session.commit()
            print(f'task added {task.id}')