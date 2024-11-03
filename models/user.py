#!/usr/bin/env python
"""
The users module defines the user model/entity
"""
from datetime import datetime

from sqlalchemy import Column, String, BigInteger, TIMESTAMP
from sqlalchemy.sql import func

from models.basemodel import Base, BaseModel


class User(Base):
    """
    The user model defines the user entity
    """
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(255), nullable=True)
    email = Column(String(255), nullable=False, unique=True)
    country_id = Column(BigInteger, nullable=False, default=1)
    email_verified_at = Column(TIMESTAMP, nullable=True)
    password = Column(String(255), nullable=False)
    remember_token = Column(String(100), nullable=True)
    google_id = Column(String(255), nullable=True)
    otp = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    def __init__(self, name, phone, email, country_id, password, google_id=None, otp=None, email_verified_at=None,
                 remember_token=None, **kwargs):
        super().__init__(**kwargs)
        if kwargs:
            for key,value in kwargs.items():
                setattr(self, key, value)
        self.name = name
        self.phone = phone
        self.email = email
        self.country_id = country_id
        self.password = password
        self.google_id = google_id
        self.otp = otp
        self.email_verified_at = email_verified_at
        self.remember_token = remember_token

    def to_dict(self):
        """
        Converts the model instance into a dictionary format.
        """
        obj = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        obj["created_at"] = self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        obj["updated_at"] = self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        if "start_date" in self.__dict__:
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
    
    @classmethod
    def bulk_insert(cls, data_list):
        from models import storage
        try:
            storage.bulk_insert(cls=cls, data_list=data_list)
        except Exception as e:
            print(f"Error Inserting bulk: {e}")
