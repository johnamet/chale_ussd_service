#!/usr/bin/env python
"""
The users module defines the user model/entity
"""
from sqlalchemy import Column, String, BigInteger, TIMESTAMP
from sqlalchemy.sql import func

from models.basemodel import Base, BaseModel


class User(BaseModel, Base):
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
        self.name = name
        self.phone = phone
        self.email = email
        self.country_id = country_id
        self.password = password
        self.google_id = google_id
        self.otp = otp
        self.email_verified_at = email_verified_at
        self.remember_token = remember_token
