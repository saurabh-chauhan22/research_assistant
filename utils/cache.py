import json
import logging

import hashlib
from redis import Redis

logger = logging.getLogger("redis_cache")

# Log "cache not available" only once per process to avoid spam when Redis is down
_unavailable_warned: bool = False

class QueryCache:
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client
    
    def _helper(self, query:str):
        assert query is not None, "Query cannot be None"
        
        query = query.strip().lower()        
        return query
    
    def _hash_query(self, query:str):
        '''
        Hash the query using SHA-256.
        '''
        assert query is not None, "Query cannot be None"
        
        normalized = self._helper(query)
        digest = hashlib.sha256(normalized.encode('utf-8')).hexdigest()
        return f"query_cache:{digest}"
        
    
    def get_cached_result(self, query: str):
        '''
        Get a cached result from the cache.
        '''
        assert query is not None, "Query cannot be None"
        
        cached_result = None
        
        if not self.is_cache_available:
            return cached_result
        cache_key = self._hash_query(query)
        
        cached_result = self.redis_client.get(cache_key)
        if cached_result:
            cached_result = json.loads(cached_result)
        return cached_result
    
    def set_cached_result(self, query: str, result: dict):
        '''
        Set a cached result in the cache.
        '''
        assert query is not None, "Query cannot be None"
        assert result is not None, "Result cannot be None"
        
        cache_key = self._hash_query(query)
        self.redis_client.set(cache_key, json.dumps(result))
        self.redis_client.expire(cache_key, 60 * 60 * 24)
        
    @property
    def is_cache_available(self) -> bool:
        '''
        Check if the cache is available.
        '''
        available = False
        try:
            available = self.redis_client.ping()
        except Exception as e:
            global _unavailable_warned
            if not _unavailable_warned:
                _unavailable_warned = True
                logger.warning("Cache is not available. Redis unreachable (%s). Start Redis (e.g. redis-server) to enable response caching.", type(e).__name__)
        return available
        
        
        