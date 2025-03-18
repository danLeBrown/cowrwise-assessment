import json
from redis import Redis
from typing import Any, Optional

class RedisService:
    def __init__(self, client: Redis):
        self.client = client

    # def publish(self, channel: str, message: dict) -> int:
    #     """Publish a message to a channel"""
    #     return self.client.publish(channel, json.dumps(message))

    # def get(self, key: str) -> Optional[Any]:
    #     """Get a value from Redis"""
    #     value = self.client.get(key)
    #     return json.loads(value) if value else None

    # def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
    #     """Set a value in Redis with optional expiration"""
    #     return self.client.set(key, json.dumps(value), ex=ex)

    # def delete(self, key: str) -> bool:
    #     """Delete a key from Redis"""
    #     return bool(self.client.delete(key))

    # def subscribe(self, channel: str):
    #     """Subscribe to a channel"""
    #     pubsub = self.client.pubsub()
    #     pubsub.subscribe(channel)
    #     return pubsub

    # def flushall(self) -> bool:
    #     """Clear all data in Redis (use carefully!)"""
    #     return bool(self.client.flushall())

    def ping(self) -> bool:
        """Ping Redis to check connection"""
        return bool(self.client.ping())