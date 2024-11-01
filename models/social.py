#!/usr/bin/env python3
"""
The social module defines the social model
"""

from sqlalchemy import Column, String, BigInteger, ForeignKey

from models.basemodel import BaseModel, Base


class Social(BaseModel, Base):
    """
    The Social model defines the social model of the user,
     i.e. the social media accounts of users
     :param name: The name of the social media platform
     :param user_id: The is of the user with the account
     :param handle: The social media handle, i.e. the username of the
     account of the related user
    """

    __tablename__ = 'socials'

    platform = Column(String(255), nullable=False)
    user_id = Column(BigInteger, nullable=False)
    handle = Column(String(255), nullable=False, unique=True)


    def __init__(self, platform, user_id, handle, **kwargs):
        super().__init__(**kwargs)
        self.platform = platform
        self.user_id = user_id
        self.handle = handle