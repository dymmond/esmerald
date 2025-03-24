import sqlite3
import time

conn = sqlite3.connect(":memory:")
cursor = conn.cursor()
cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
cursor.execute("INSERT INTO users (name) VALUES ('Alice')")
conn.commit()


def get_user_slow(user_id: int):
    time.sleep(2)  # Simulating slow DB query
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()


# Slow execution
print(get_user_slow(1))
print(get_user_slow(1))
