from fastapi import FastAPI
from schema import schema, get_context_value
from ariadne.asgi import GraphQL

app = FastAPI()

# single endpoint
app.mount('/graphql', GraphQL(schema, debug=True, context_value=get_context_value))


@app.get("/")
async def root():
    return {"message": "Hello World"}