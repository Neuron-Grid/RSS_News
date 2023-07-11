import redis
import time

# Redisへの接続を作成
def get_redis_connection():
    return redis.Redis(host='127.0.0.1', port=6379, db=2)

# Zsetにフィードを追加または更新
def schedule_feed(redis_conn, feed_id, interval=300):
    next_update = time.time() + interval
    redis_conn.zadd('feeds', {feed_id: next_update})

# 更新が必要なフィードを取得
def get_feeds_to_update(redis_conn):
    now = time.time()
    return redis_conn.zrangebyscore('feeds', 0, now)
