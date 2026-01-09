from ariadne import make_executable_schema, load_schema_from_path
from resolvers.query import query
from resolvers.mutations import mutation
from resolvers.type_resolvers import all_types
from engine import async_session_local, get_session
from aiodataloader import DataLoader
from dataloaders import batch_load_posts

# core GraphQL server setup:
# 1. Load GraphQL schema
type_def = load_schema_from_path('schema.graphql')
# 2. Bind resolvers to schema
schema = make_executable_schema(
    type_def,
    [query, *all_types, mutation]
)

"""
# Context function - runs for each request
async def get_context_value(request):
    session = async_session_local()
    # session = await anext(get_session())
    print('session!!!', session)
    token = request.headers.get('Authorization')
    print('token', token)
    # current_user = decode(token)
    return {
        "session": session,
        "request": request,
        # "current_user": current_user,
        "user_posts_loader": DataLoader(batch_load_posts)
    }
"""
  
# even better: Close Session After Request using Ariadne's built-in support
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_context_value(request):
    session = async_session_local()
    try:
        yield {
            "session": session,
            "request": request,
            "user_posts_loader": DataLoader(batch_load_posts)
        }
    finally:
        await session.close()