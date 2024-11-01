from models.engine.cache_engine import Cache
from models.engine.db_storage import DBStorage

storage = DBStorage()

storage.reload()

cache = Cache()
