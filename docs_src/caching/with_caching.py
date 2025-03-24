import sqlite3
import time

conn = sqlite3.connect(":memory:")
cursor = conn.cursor()
cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
cursor.execute("INSERT INTO users (name) VALUES ('Alice')")
conn.commit()


cache_store = {}


def get_user_fast(user_id: int):
    if user_id in cache_store:
        print("Returning from cache")
        return cache_store[user_id]

    time.sleep(2)  # Simulating slow DB query
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    cache_store[user_id] = result
    return result


# First call is slow, second call is instant
print(get_user_fast(1))
print(get_user_fast(1))
