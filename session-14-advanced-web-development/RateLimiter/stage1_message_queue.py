from fastapi import FastAPI, Depends, HTTPException, Header
from celery import Celery
from celery.result import AsyncResult
import uuid
from typing import Optional
from stage1_Basic_rate_limiter import RateLimiter

# Configure Celery
app_celery = Celery(
    'orders',
    broker='amqp://localhost',
    backend='redis://localhost:6379/0'
)

app_celery.conf.update(
    task_serializer="json",
    accept_content=['json'],
    result_serializer='json'
)

app = FastAPI()

# Create rate limiter instances
# Different limits for different endpoints
order_limiter = RateLimiter(max_requests=5, window_seconds=60)  # 5 orders per minute
status_limiter = RateLimiter(max_requests=20, window_seconds=60)  # 20 status checks per minute

# Helper function to get user ID from header or IP
def get_user_id(
    x_user_id: Optional[str] = Header(None),
    x_forwarded_for: Optional[str] = Header(None)
) -> str:
    """
    Get user identifier from header or IP address.
    Priority: x-user-id > x-forwarded-for > "anonymous"
    """
    if x_user_id:
        return x_user_id
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]  # First IP in chain
    return "anonymous"

@app.post('/orders')
def create_order(
    customer: str,
    amount: float,
    user_id: str = Depends(get_user_id)
):
    """Create order with rate limiting"""
    
    # Check rate limit
    order_limiter.check_or_raise(user_id)
    
    # Create order
    order_id = str(uuid.uuid4())[:10]
    
    # Queue task
    task = app_celery.send_task(
        'process_order',
        args=[order_id, customer, amount]
    )
    
    return {
        'status': 'processing',
        'order_id': order_id,
        'task_id': task.id,
        'message': f'Order queued successfully'
    }

@app.get('/orders/{task_id}/status')
def check_status(
    task_id: str,
    user_id: str = Depends(get_user_id)
):
    """Check order status with rate limiting"""
    
    # Check rate limit
    status_limiter.check_or_raise(user_id)
    
    # Check task status
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

@app.get('/rate-limit/info')
def rate_limit_info(user_id: str = Depends(get_user_id)):
    """Get rate limit info for user (debugging)"""
    now = time.time()
    cutoff = now - order_limiter.window_seconds
    
    order_requests = order_limiter.user_requests.get(user_id, [])
    recent_orders = [ts for ts in order_requests if ts > cutoff]
    
    status_requests = status_limiter.user_requests.get(user_id, [])
    recent_status = [ts for ts in status_requests if ts > cutoff]
    
    return {
        'user_id': user_id,
        'orders': {
            'used': len(recent_orders),
            'limit': order_limiter.max_requests,
            'window_seconds': order_limiter.window_seconds,
            'remaining': order_limiter.max_requests - len(recent_orders)
        },
        'status_checks': {
            'used': len(recent_status),
            'limit': status_limiter.max_requests,
            'window_seconds': status_limiter.window_seconds,
            'remaining': status_limiter.max_requests - len(recent_status)
        }
    }