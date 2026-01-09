from fastapi import FastAPI
from celery import Celery
import uuid
# from .message_consumer import process_order
from celery.result import AsyncResult  

app_celery = Celery(
    'orders',
    broker='amqp://localhost',
    # backend='rpc://'
    backend='redis://localhost:6379/0'
)

app_celery.conf.update(
    task_serializer="json",
    accept_content=['json'],  # Ignore other content
    result_serializer='json'
)

app = FastAPI()


@app.post('/orders')
def create_order(customer: str, amount: float):
    order_id = str(uuid.uuid4())[:10]
    # result = process_order(order_id, customer, amount)
    # return result
    # task = process_order.delay(order_id, customer, amount)

    # Send task by name (no import needed!)
    task = app_celery.send_task(
        'process_order',  # Must match task name in message_consumer.py
        args=[order_id, customer, amount]
    )
    
    return {
        'status': 'processing',
        'order_id': order_id,
        'task_id': task.id
    }
    
@app.get('/orders/{task_id}/status')
def check_status(task_id: str):
    """Check if order processing is complete"""
    task = AsyncResult(task_id, app=app_celery)
    
    if task.ready():
        # Task finished
        if task.successful():
            return {
                'task_id': task_id,
                'status': 'completed',
                'result': task.result
            }
        else:
            return {
                'task_id': task_id,
                'status': 'failed',
                'error': str(task.info)
            }
    else:
        # Still processing or pending
        return {
            'task_id': task_id,
            'status': task.state,  # Use actual state: PENDING, STARTED
            'ready': False
        }