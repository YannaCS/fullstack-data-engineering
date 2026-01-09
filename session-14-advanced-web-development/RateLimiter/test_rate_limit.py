# test_rate_limit.py
import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def test_rate_limit():
    """Test rate limiting on order creation"""
    
    print("Testing rate limit (5 requests per 60 seconds)...")
    
    for i in range(7):
        try:
            response = requests.post(
                f"{BASE_URL}/orders",
                params={"customer": f"Alice", "amount": 99.99},
                headers={"X-User-Id": "test-user-123"}
            )
            
            if response.status_code == 200:
                print(f"Request {i+1}: ✅ Success - {response.json()}")
            elif response.status_code == 429:
                print(f"Request {i+1}: ⛔ Rate limited - {response.json()}")
                retry_after = response.headers.get('Retry-After', 'unknown')
                print(f"  Retry after: {retry_after} seconds")
            else:
                print(f"Request {i+1}: ❌ Error {response.status_code}")
                
        except Exception as e:
            print(f"Request {i+1}: ❌ Exception - {e}")
        
        time.sleep(0.5)  # Small delay between requests

def test_token_bucket():
    """Test token bucket rate limiter"""
    
    print("\nTesting token bucket (capacity=10, refill=2/sec)...")
    
    # Burst: Use all 10 tokens quickly
    print("Phase 1: Burst of 10 requests")
    for i in range(12):
        response = requests.post(
            f"{BASE_URL}/orders",
            params={"customer": "Bob", "amount": 50.0},
            headers={"X-User-Id": "burst-user"}
        )
        
        if response.status_code == 200:
            data = response.json()
            tokens = data.get('rate_limit_info', {}).get('remaining_tokens', '?')
            print(f"  Request {i+1}: ✅ Success (tokens left: {tokens})")
        else:
            print(f"  Request {i+1}: ⛔ Rate limited")
    
    # Wait for refill
    print("\nPhase 2: Wait 2 seconds (should gain ~4 tokens)")
    time.sleep(2)
    
    # Try again
    for i in range(5):
        response = requests.post(
            f"{BASE_URL}/orders",
            params={"customer": "Bob", "amount": 50.0},
            headers={"X-User-Id": "burst-user"}
        )
        
        if response.status_code == 200:
            print(f"  Request {i+1}: ✅ Success")
        else:
            print(f"  Request {i+1}: ⛔ Rate limited")

if __name__ == "__main__":
    test_rate_limit()
    test_token_bucket()

"""
Run Test:
# Terminal 1: Start services
docker start redis rabbitmq
celery -A message_consumer worker --loglevel=info

# Terminal 2: Start FastAPI
fastapi dev message_queue.py

# Terminal 3: Run test
python test_rate_limit.py
"""