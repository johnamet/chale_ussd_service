#!/usr/bin/env python3
"""
The BaseModel class for all models, providing common attributes and methods
like id, timestamps, and CRUD operations.
"""

import datetime
from sqlalchemy import TIMESTAMP, BigInteger, Column, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaseModel(Base):
    """
    The BaseModel class provides common attributes and CRUD operations for all derived models.
    """

    __abstract__ = True  # Indicate this is an abstract base class

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP, nullable=True, default=None)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        """
        Converts the model instance into a dictionary format.
        """
        obj = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        obj["created_at"] = self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        obj["updated_at"] = self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        obj["deleted_at"] = self.deleted_at.strftime('%Y-%m-%d %H:%M:%S') if self.deleted_at else None
        obj["start_date"] = self.start_date.strftime('%Y-%m-%d') if self.start_date else None
        obj["start_time"] = self.start_date.strftime('%H:%M:%S') if self.start_time else None
        obj["end_date"] = self.end_date.strftime('%Y-%m-%d') if self.end_date else None
        obj["end_time"] = self.end_time.strftime('%H:%M:%S') if self.end_time else None


        return obj

    def delete(self):
        self.deleted_at = datetime.datetime.now(datetime.timezone.utc)
        self.save()

    def save(self):
        from models import storage
        try:
            storage.new(self)
            storage.save()
        except Exception as e:
            # Handle exceptions (log them, re-raise, etc.)
            print(f"Error saving model: {e}")


    def update(self):
        from models import storage
        try:
            storage.save()
        except Exception as e:
            # Handle exceptions (log them, re-raise, etc.)
            print(f"Error updating model: {e}")

    @classmethod
    def all(cls, page=None, page_size=10):
        from models import storage
        return storage.all(cls, page=page, page_size=page_size)
    
    @classmethod
    def all_valid(cls, page=None, page_size=10):
        from models import storage
        return storage.all_valid(cls, page, page_size)

    @classmethod
    def get(cls, _id):
        from models import storage
        return storage.get(cls, _id)

    @classmethod
    def get_by_name(cls, name):
        from models import storage
        return storage.get_by_name(cls, name)

    @classmethod
    def count(cls):
        from models import storage
        return storage.count(cls=cls)
    
    @classmethod
    def dynamic_query(cls, filters=None, page=None, page_size=10):
        from models import storage
        return storage.dynamic_query(cls, filters=filters, page=page,
                                     page_size=page_size)
