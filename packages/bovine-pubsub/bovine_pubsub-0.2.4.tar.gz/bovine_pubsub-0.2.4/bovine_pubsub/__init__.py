from .redis import RedisBovinePubSub
from .queue import QueueBovinePubSub


async def configure_bovine_pub_sub(app):
    if "REDIS_URI" in app.config:
        app.config["bovine_pub_sub"] = RedisBovinePubSub()
    else:
        app.config["bovine_pub_sub"] = QueueBovinePubSub()
