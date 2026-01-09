from ariadne import MutationType
from models import User
from sqlalchemy import select
from graphql import GraphQLError

mutation = MutationType()

@mutation.field('createUser')
async def resolve_create_user(_, info, name, email):
    session = info.context.get('session')
    existing_user = await session.execute(select(User).where(User.email == email))
    print('existing_user', existing_user)
    if existing_user.scalar():
        raise GraphQLError('user already existed')
    
    new_user = User(name=name, email=email)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user

