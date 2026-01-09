# Stage 2: Token Bucket Rate Limiter (O(1) Performance)
from collections import defaultdict
from typing import Dict
import time
from fastapi import HTTPException

class RateLimiter:
    """Sliding window rate limiter - O(n) time complexity"""
    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.user_requests: Dict[str, list] = defaultdict(list)
    
    def allow_request(self, user_id: str) -> bool:
        now = time.time()
        requests = self.user_requests[user_id]
        cutoff_time = now - self.window_seconds
        requests[:] = [ts for ts in requests if ts > cutoff_time]
        
        if len(requests) < self.max_requests:
            requests.append(now)
            return True
        return False
    
    def check_or_raise(self, user_id: str):
        if not self.allow_request(user_id):
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Max {self.max_requests} requests per {self.window_seconds} seconds.",
                headers={"Retry-After": str(self.window_seconds)}
            )


class TokenBucketRateLimiter:
    """Token bucket rate limiter - O(1) time complexity"""
    def __init__(self, capacity: int, refill_rate: float) -> None:
        """
        capacity: Maximum number of tokens in bucket
        refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.user_buckets: Dict[str, Dict[str, float]] = {}
    
    def allow_request(self, user_id: str) -> bool:
        """O(1) time complexity"""
        now = time.time()
        
        # Initialize bucket for new user
        if user_id not in self.user_buckets:
            self.user_buckets[user_id] = {
                'tokens': self.capacity,
                'last_refill': now
            }
        
        bucket = self.user_buckets[user_id]
        
        # Calculate tokens to add based on elapsed time
        time_elapsed = now - bucket['last_refill']
        tokens_to_add = time_elapsed * self.refill_rate
        
        # Refill bucket (up to capacity)
        bucket['tokens'] = min(self.capacity, bucket['tokens'] + tokens_to_add)
        bucket['last_refill'] = now
        
        # Try to consume 1 token
        if bucket['tokens'] >= 1:
            bucket['tokens'] -= 1
            return True
        
        return False
    
    def check_or_raise(self, user_id: str):
        """Check rate limit and raise HTTPException if exceeded"""
        if not self.allow_request(user_id):
            # Calculate retry after time
            bucket = self.user_buckets.get(user_id)
            if bucket:
                time_to_token = (1 - bucket['tokens']) / self.refill_rate
                retry_after = max(1, int(time_to_token))
            else:
                retry_after = 1
            
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Bucket capacity: {self.capacity}, refill rate: {self.refill_rate} tokens/sec",
                headers={"Retry-After": str(retry_after)}
            )
    
    def get_info(self, user_id: str) -> dict:
        """Get rate limit info for debugging"""
        if user_id not in self.user_buckets:
            return {
                'tokens': self.capacity,
                'capacity': self.capacity,
                'refill_rate': self.refill_rate
            }
        
        # Update tokens before returning info
        self.allow_request(user_id)  # This updates tokens
        bucket = self.user_buckets[user_id]
        
        return {
            'tokens': bucket['tokens'],
            'capacity': self.capacity,
            'refill_rate': self.refill_rate
        }