from fastapi import FastAPI, Header, Query, Path, Body
from typing import Optional
from app.schemas import Notebase
from app.routers.notes import router as notes_router
from app.routers.auth import router as auth_router
from dotenv import load_dotenv

# load env variables
load_dotenv()

app = FastAPI(
    title="fast api project"
)

app.include_router(notes_router)
app.include_router(auth_router)




@app.get('/')
def home():
    return {'message': 'hello world'}


@app.get('/items/{item_id}')
def get_item(
    item_id: int = Path(description="item id to query"),
    limit: Optional[int] = Query(None, lt=100, description="max items to return"),
    user_agent: str = Header(...),
):
    '''
    This api is to fetch item by id
    '''
    
    return {
        'item_id': item_id,
        'limit': limit,
        'user_agent': user_agent
    }
    
@app.post('/test-validation')    
def test_validation(
    note: Notebase = Body(...)
):
    return {
        'recevied': note.model_dump()
    }
    
