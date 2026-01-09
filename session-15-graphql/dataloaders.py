
from engine import async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Post

async def batch_load_posts(user_ids):
    '''
    input :[1, 2, 3, 4]
    
    output:[
        [post1, post2],
        [post3, post4],
        [],
        [post5]
    ]
    '''
    async with AsyncSession(async_engine) as session:
        print('load post!!!')
        stmt = select(Post).where(Post.author_id.in_(user_ids))
        posts = await session.execute(stmt)
        posts = posts.scalars().all()
        
        '''
        {
            1: [post1, post2],
            2: [post3, post4],
            3: []
        }
        '''
        posts_by_author = {}
        
        for post in posts:
            if post.author_id not in posts_by_author:
                posts_by_author[post.author_id] = []
                
            posts_by_author[post.author_id].append(post)
        
        
        result = [posts_by_author.get(user_id, []) for user_id in user_ids]
        return result
    