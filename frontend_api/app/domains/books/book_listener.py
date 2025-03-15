# frontend_api/app/domains/books/book_listener.py
import redis

redis_client = redis.Redis(host="redis", port=6379, db=0)
pubsub = redis_client.pubsub()
pubsub.subscribe("book_added")

for message in pubsub.listen():
    if message["type"] == "message":
        book_id = message["data"]
        # Fetch the book from the admin database and add it to the frontend database
        pass