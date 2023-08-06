from upstash_redis.client import Redis
from asyncio import run

redis = Redis.from_env()


async def main():
    async with redis:
        await redis.set("a", "b")
        print(await redis.get("a"))

run(main())
