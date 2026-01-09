from collections import defaultdict
from typing import Dict, List
import time
from fastapi import HTTPException

class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int) -> None:
        """
        max_requests: Maximum number of requests allowed
        window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # Store list of request timestamps for each user
        self.user_requests: Dict[str, List[float]] = defaultdict(list)
    
    def allow_request(self, user_id: str) -> bool:
        """
        Check if user can make a request.
        Returns True if allowed, False if rate limited.
        """
        now = time.time()
        
        # Get user's request history
        requests = self.user_requests[user_id]
        
        # Remove timestamps outside the current window
        cutoff_time = now - self.window_seconds
        requests[:] = [ts for ts in requests if ts > cutoff_time]
        
        # Check if under the limit
        if len(requests) < self.max_requests:
            requests.append(now)
            return True
        
        return False
    
    def check_or_raise(self, user_id: str):
        """
        Check rate limit and raise HTTPException if exceeded.
        Use this as a dependency in FastAPI.
        """
        if not self.allow_request(user_id):
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Max {self.max_requests} requests per {self.window_seconds} seconds."
            )