import time

cache_store = {}


def expensive_computation(x: int) -> int:
    if x in cache_store:
        print("Returning cached result")
        return cache_store[x]

    print("Performing expensive computation...")
    time.sleep(3)  # Simulating a slow operation
    result = x * x
    cache_store[x] = result
    return result


# First call (slow)
print(expensive_computation(10))  # Computes and stores result

# Second call (fast)
print(expensive_computation(10))  # Fetches from cache
