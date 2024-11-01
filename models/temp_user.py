#!/usr/bin/env python3


from sqlalchemy import Column, Integer, String, BigInteger, TIMESTAMP, func

from models.basemodel import BaseModel, Base
from models.user import User


class TempUser(BaseModel, Base):

    __tablename__ = 'temp_users'
    instagram = Column(String, nullable=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(255), nullable=True)
    email = Column(String(255), nullable=False, unique=True)
    country_id = Column(BigInteger, nullable=False, default=1)
    email_verified_at = Column(TIMESTAMP, nullable=True)
    password = Column(String(255), nullable=False)
    remember_token = Column(String(100), nullable=True)
    google_id = Column(String(255), nullable=True)
    otp = Column(String(255), nullable=True)

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