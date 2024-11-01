#!/usr/bin/env python3
"""
Cache Management System using Redis

This module provides a Redis-based cache engine for managing temporary data storage.
It is designed to support caching needs for event ticketing services, allowing
for efficient data retrieval and updates.
"""

import os
from typing import Dict, Union, List, Optional

import redis

# Redis connection parameters from environment variables
_CACHE_HOST = os.getenv('REDIS_HOST', 'localhost')
_CACHE_PORT = int(os.getenv('REDIS_PORT', 6379))
_CACHE_DB = int(os.getenv('REDIS_DB', 0))


class Cache:
    """Redis-based cache management system for storing and retrieving data."""

    def __init__(self):
        """Initializes the Redis client with connection parameters."""
        self.__client = redis.Redis(host=_CACHE_HOST, port=_CACHE_PORT, db=_CACHE_DB)

    def ping(self) -> bool:
        """
        Checks the Redis connection by pinging the server.

        Returns:
            bool: True if the Redis server is reachable, False otherwise.
        """
        try:
            return self.__client.ping()
        except Exception as e:
            print(f"Error connecting to Redis server: {e}")
            return False

    def hset(self, key: str, data: Dict) -> bool:
        """
        Sets multiple fields in a hash stored at `key`.

        Parameters:
            key (str): The Redis key under which the hash is stored.
            data (Dict): A dictionary mapping fields to values to store in the hash.

        Returns:
            bool: True if the operation is successful, False otherwise.
        """
        try:
            self.__client.hset(name=key, mapping=data)
            return True
        except Exception as e:
            print(f"Error setting hash set in Redis: {e}")
            return False

    def hget_all(self, key: str) -> Optional[Dict[str, str]]:
        """
        Retrieves all fields and values in a hash stored at `key` and decodes the byte strings to regular strings.

        Parameters:
            key (str): The Redis key of the hash to retrieve.

        Returns:
            Dict[str, str]: Dictionary of field-value pairs with decoded strings if key exists, None if error occurs.
        """
        try:
            data = self.__client.hgetall(key)
            # Decode byte strings to regular strings
            return {k.decode('utf-8'): v.decode('utf-8') for k, v in data.items()}
        except Exception as e:
            print(f"Error retrieving hash set from Redis: {e}")
            return None

    def set(self, key: str, value: Union[str, bytes], expire: Optional[int] = None) -> bool:
        """
        Sets a key-value pair in Redis with optional expiration.

        Parameters:
            key (str): The Redis key to set.
            value (Union[str, bytes]): The value to store under the key.
            expire (Optional[int]): Expiration time in seconds.

        Returns:
            bool: True if the operation is successful, False otherwise.
        """
        try:
            self.__client.set(name=key, value=value, ex=expire)
            return True
        except Exception as e:
            print(f"Error setting value in Redis: {e}")
            return False

    def get(self, key: str) -> Optional[bytes]:
        """
        Retrieves the value of a given key from Redis.

        Parameters:
            key (str): The Redis key to retrieve.

        Returns:
            Optional[bytes]: The value of the key if it exists, None if the key does not exist or an error occurs.
        """
        try:
            return self.__client.get(key)
        except Exception as e:
            print(f"Error retrieving value from Redis: {e}")
            return None

    def delete(self, key: str) -> bool:
        """
        Deletes a given key from Redis.

        Parameters:
            key (str): The Redis key to delete.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        try:
            return self.__client.delete(key) > 0
        except Exception as e:
            print(f"Error deleting key from Redis: {e}")
            return False

    def exists(self, key: str) -> bool:
        """
        Checks if a given key exists in Redis.

        Parameters:
            key (str): The Redis key to check.

        Returns:
            bool: True if the key exists, False otherwise.
        """
        try:
            return self.__client.exists(key) == 1
        except Exception as e:
            print(f"Error checking existence of key in Redis: {e}")
            return False

    def expire(self, key: str, time: int) -> bool:
        """
        Sets an expiration time for a given key.

        Parameters:
            key (str): The Redis key to set an expiration for.
            time (int): Expiration time in seconds.

        Returns:
            bool: True if the expiration was set, False otherwise.
        """
        try:
            return self.__client.expire(key, time)
        except Exception as e:
            print(f"Error setting expiration for key in Redis: {e}")
            return False

    def keys(self, pattern: str = '*') -> List[bytes]:
        """
        Retrieves all keys matching a given pattern.

        Parameters:
            pattern (str): Pattern to match keys (default is '*').

        Returns:
            List[bytes]: List of keys that match the pattern.
        """
        try:
            return self.__client.keys(pattern)
        except Exception as e:
            print(f"Error retrieving keys with pattern '{pattern}' from Redis: {e}")
            return []

    def flush_db(self) -> bool:
        """
        Clears all data in the current Redis database.

        Returns:
            bool: True if the flush was successful, False otherwise.
        """
        try:
            self.__client.flushdb()
            return True
        except Exception as e:
            print(f"Error flushing Redis database: {e}")
            return False
