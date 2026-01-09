from celery import Celery
import time
import redis

app_celery = Celery(
    'orders',
    broker='amqp://localhost',
    # backend='rpc://'
    backend='redis://localhost:6379/0'  # Redis as Celery Result Backend
)

app_celery.conf.update(
    task_serializer="json",
    accept_content=['json'],  # Ignore other content
    result_serializer='json'
)

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)  # Redis for Idempotency Checking


@app_celery.task(
    name='process_order',
    autoretry_for=(Exception, ),
    retry_kwargs={'max_retries': 3},
    retry_backoff=True
)

def process_order(order_id, customer, amount):
    time.sleep(20)

    # handle idempotency
    # Check if already processed (idempotency)
    processed = redis_client.get(order_id)
    
    # Process the order
    if processed:
        # already processed
        return {'status': 'already_processed'}
    
    result = {
        'order_id': order_id,
        'customer': customer,
        'amount': amount,
        'status': 'completed'
    }  
    
    # Mark as processed
    redis_client.set(order_id, "processed")
    
    
    print(f'Order {order_id} processed complete')
    return result

