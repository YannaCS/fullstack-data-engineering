from ariadne import ObjectType
from engine import engine
from sqlalchemy.ext.asyncio import AsyncSession
from models import Post, User
from sqlalchemy import select

user_type = ObjectType('User')
post_type = ObjectType('Post')

# N+1 problem
# resolve -> dataloader -> batch loader

# first query users and all posts_ids
# second query -> query all posts for the all posts_ids
# organize all posts back to the user entity

@user_type.field('posts')
async def resolve_user_posts(user, info):
    # session = info.context.get('session')
    # print('resolve_user_posts!!!')
    # posts = await session.execute(select(Post).where(Post.author_id == user.id))  
    # return posts.scalars().all()
    posts_loader = info.context.get('user_posts_loader')
    
    return await posts_loader.load(user.id)

@post_type.field('author')
async def resolver_post_author(post, info):
    session = info.context.get('session')
    user = await session.execute(select(User).where(User.id == post.id))  
    return user.scalar()
    
all_types = [user_type, post_type]