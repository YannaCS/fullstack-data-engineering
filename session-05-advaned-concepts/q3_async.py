# QA coding q3
import asyncio
import random

def async_retry(max_attempts=3, base_delay=1, backoff_factor=2):
    """
    Decorator that retries async functions with exponential backoff.
    
    Args:
        max_attempts: Maximum number of attempts
        base_delay: Initial delay between retries (seconds)
        backoff_factor: Multiply delay by this factor after each retry
    
    Example:
        @async_retry(max_attempts=3, base_delay=1, backoff_factor=2)
        async def unreliable_function():
            # Will retry with delays: 1s, 2s, 4s
            pass
    """
    def decorator(func):
        # TODO: Implement a decorator with retrying logic with exponential backoff
        # It Will retry with delays: 1s, 2s, 4s if error raises until success
        async def wrapper(*args, **kwargs):
            delay = base_delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        # last attempt failed
                        raise
                    else:
                        print(f'[Attempt {attempt}] Failed: {e}. Retrying in {delay:.2f}s...')
                        await asyncio.sleep(delay)
                        delay *= backoff_factor
            
        return wrapper
    return decorator


# Flaky API simulator
@async_retry(max_attempts=5, base_delay=0.5, backoff_factor=2)
async def flaky_api_call(success_rate=0.3):
    """
    Simulates an unreliable API call.
    
    Args:
        success_rate: Probability of success (0.0 to 1.0)
    """
    print(f"  Attempting API call...")
    await asyncio.sleep(0.1)  # Simulate network delay
    
    if random.random() < success_rate:
        print("Success!")
        return "API response data"
    else:
        print("Failed!")
        raise ConnectionError("API temporarily unavailable")


async def test_retry():
    print("Test 1: Flaky API (30% success rate)")
    try:
        result = await flaky_api_call(success_rate=0.3)
        print(f"Final result: {result}\n")
    except ConnectionError as e:
        print(f"All retries failed: {e}\n")
    
    print("Test 2: Very flaky API (10% success rate)")
    try:
        result = await flaky_api_call(success_rate=0.1)
        print(f"Final result: {result}\n")
    except ConnectionError as e:
        print(f"All retries failed: {e}\n")


# Run test
if __name__ == "__main__":
    asyncio.run(test_retry())
