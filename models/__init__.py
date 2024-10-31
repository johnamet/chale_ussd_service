from models.engine.db_storage import DBStorage
from models.engine.cache_engine import Cache

storage = DBStorage()

storage.reload()


cache = Cache()