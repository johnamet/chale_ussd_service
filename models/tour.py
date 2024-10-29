#!/usr/bin/env python
"""
The tours module defines the tour model/entity.
"""
from sqlalchemy import Column, String, Integer, BigInteger, Numeric, Date, Time, Text
from models.basemodel import BaseModel, Base

class Tour(BaseModel, Base):
    """
    The Tour model defines the tour entity.
    """
    __tablename__ = 'tours'

    name = Column(String(255), unique=True, nullable=False)
    images = Column(Text, nullable=False)
    location = Column(String(255), nullable=False)
    pickup_date = Column(Date, nullable=False)
    pickup_time = Column(Time, nullable=False)
    end_date = Column(Date, nullable=False)
    end_time = Column(Time, nullable=False)
    seats = Column(Integer, nullable=False)
    country_id = Column(BigInteger, nullable=False)
    region_id = Column(BigInteger, nullable=False)
    more_info = Column(Text, nullable=False)
    cancellation_policy = Column(String(255), default="No cancellation", nullable=False)
    tour_guide_languages = Column(String(255), nullable=False)
    wheel_chair_accessible = Column(String(255), nullable=True)
    highlights = Column(Text, nullable=False)
    includes = Column(Text, nullable=False)
    meeting_point = Column(Text, nullable=False)
    know_before_you_go = Column(Text, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    approved_by = Column(BigInteger, nullable=True)
    status = Column(String(255), default="pending", nullable=False)
    service_charge = Column(Numeric(10, 2), default=0.00, nullable=True)

    def __init__(self, name, images, location, pickup_date, pickup_time, end_date, end_time, seats, country_id,
                 region_id, more_info, cancellation_policy, tour_guide_languages, wheel_chair_accessible, highlights,
                 includes, meeting_point, know_before_you_go, user_id, approved_by, status, service_charge, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.images = images
        self.location = location
        self.pickup_date = pickup_date
        self.pickup_time = pickup_time
        self.end_date = end_date
        self.end_time = end_time
        self.seats = seats
        self.country_id = country_id
        self.region_id = region_id
        self.more_info = more_info
        self.cancellation_policy = cancellation_policy
        self.tour_guide_languages = tour_guide_languages
        self.wheel_chair_accessible = wheel_chair_accessible
        self.highlights = highlights
        self.includes = includes
        self.meeting_point = meeting_point
        self.know_before_you_go = know_before_you_go
        self.user_id = user_id
        self.approved_by = approved_by
        self.status = status
        self.service_charge = service_charge
