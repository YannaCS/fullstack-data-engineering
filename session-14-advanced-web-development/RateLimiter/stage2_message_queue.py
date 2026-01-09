from fastapi import FastAPI, Depends, Header
from stage2_TokenBucket_rate_limiter import TokenBucketRateLimiter
import uuid

app = FastAPI()

# Token bucket rate limiters
# Capacity=10, refill 2 tokens/second
order_limiter = TokenBucketRateLimiter(capacity=10, refill_rate=2.0)
# Capacity=50, refill 5 tokens/second
status_limiter = TokenBucketRateLimiter(capacity=50, refill_rate=5.0)

def get_user_id(x_user_id: str = Header(None)) -> str:
    return x_user_id or "anonymous"

@app.post('/orders')
def create_order(
    customer: str,
    amount: float,
    user_id: str = Depends(get_user_id)
):
    """Create order with token bucket rate limiting"""
    order_limiter.check_or_raise(user_id)
    
    order_id = str(uuid.uuid4())[:10]
    task = app_celery.send_task('process_order', args=[order_id, customer, amount])
    
    # Get current token info for response headers
    token_info = order_limiter.get_info(user_id)
    
    return {
        'status': 'processing',
        'order_id': order_id,
        'task_id': task.id,
        'rate_limit_info': {
            'remaining_tokens': int(token_info['tokens']),
            'capacity': token_info['capacity'],
            'refill_rate': token_info['refill_rate']
        }
    }

@app.get('/orders/{task_id}/status')
def check_status(
    task_id: str,
    user_id: str = Depends(get_user_id)
):
    """Check status with token bucket rate limiting"""
    status_limiter.check_or_raise(user_id)
    
    task = AsyncResult(task_id, app=app_celery)
    
    if task.ready():
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
        return {
            'task_id': task_id,
            'status': task.state,
            'ready': False
        }