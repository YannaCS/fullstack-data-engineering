# For production with multiple servers, use Redis
import redis
import time
from fastapi import HTTPException

class RedisRateLimiter:
    """Redis-based rate limiter for distributed systems"""
    
    def __init__(self, redis_client: redis.Redis, max_requests: int, window_seconds: int):
        self.redis = redis_client
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    def allow_request(self, user_id: str) -> bool:
        """Using Redis sorted set for sliding window"""
        key = f"rate_limit:{user_id}"
        now = time.time()
        window_start = now - self.window_seconds
        
        # Use Redis pipeline for atomic operations
        pipe = self.redis.pipeline()
        
        # Remove old entries
        pipe.zremrangebyscore(key, 0, window_start)
        
        # Count requests in current window
        pipe.zcard(key)
        
        # Add current request
        pipe.zadd(key, {str(now): now})
        
        # Set expiration
        pipe.expire(key, self.window_seconds)
        
        # Execute pipeline
        results = pipe.execute()
        
        request_count = results[1]
        
        return request_count < self.max_requests
    
    def check_or_raise(self, user_id: str):
        if not self.allow_request(user_id):
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded",
                headers={"Retry-After": str(self.window_seconds)}
            )

# Usage in FastAPI
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
rate_limiter = RedisRateLimiter(redis_client, max_requests=100, window_seconds=60)

@app.post('/orders')
def create_order(customer: str, amount: float, user_id: str = Depends(get_user_id)):
    rate_limiter.check_or_raise(user_id)
    # ... rest of code