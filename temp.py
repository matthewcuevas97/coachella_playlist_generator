import redis

redis_client = redis.Redis()
redis_client.mset({"Croatia": "Zagreb", "Bahamas": "Nassau"})
argarg = redis_client.get("Croatia")
print(argarg)