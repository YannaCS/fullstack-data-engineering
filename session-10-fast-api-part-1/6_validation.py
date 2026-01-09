from fastapi import FastAPI, Header, Query, Path, Body

app = FastAPI(
    title="fast api project"
)

@app.get('/')
def home():
    return {'message': 'hello world'}

@app.get('/items/{item_id}')
def get_item(
    # with validation: 
    item_id: int = Path(..., description='Item id in path'), 
    limit: int | None=Query(None, lt=100, description='max items to return'),
    user_agent: str = Header(...)
):
    '''
    This api is to fetch item by id
    '''
    return {
        'the input item id: ': item_id,
        'limit': limit,
        'user_agent': user_agent
    }

from validation_schemas import Notebase
@app.post('/test-validation')
def test_validation(note:Notebase):
    return {
        'received': note.model_dump()
    }
    
# fastapi can auto clarify where to fetch variable, 
# so do not need to declare note:Notebase=Body(...):
# def test_validation(note:Notebase=Body(...)):
#     return {
#         'received': note.model_dump()
#     }