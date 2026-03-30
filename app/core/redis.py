import os

import redis

from app.core.config import settings

if os.getenv("PYTEST_USE_FAKE_REDIS"):
    import fakeredis

    redis_client = fakeredis.FakeRedis(decode_responses=True)
else:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
