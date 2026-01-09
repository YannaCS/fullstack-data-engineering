import redis
from functools import wraps
import time
import json

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

def cache(ttl=3600):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{args}:{kwargs}"
            
            cached = redis_client.get(cache_key)
            
            if cached:
                print('[Cache HIT]')
                return json.loads(cached)

            print('[Cache MISS]')
            result = func(*args, **kwargs)
            
            redis_client.set(cache_key, json.dumps(result), ttl)
            
            return result
            
        return wrapper
    return decorator

@cache(ttl=1)
def get_user(user_id):
    print('fetch from database...')
    time.sleep(2)  # simulate to get data from database
    return {"user_id": user_id}

start = time.time()
print(get_user(1))
print(f"Time used: {time.time() - start:.4f} seconds")
start = time.time()
print(get_user(1))
print(f"Time used: {time.time() - start:.4f} seconds")
start = time.time()
print(get_user(1))
print(f"Time used: {time.time() - start:.4f} seconds")

# Disconnect
redis_client.close()  # closes the connection pool