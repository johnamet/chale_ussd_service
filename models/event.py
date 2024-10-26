#!/usr/bin/env python
"""
The events module defines the event mode/ entity
"""
from sqlalchemy import Column, String, Integer, Numeric, Date, Time, Text

from models.basemodel import BaseModel, Base


class Event(BaseModel, Base):
    """
    The event model defines the event mode/ entity
    :args
    """
    __tablename__ = 'events'

    name = Column(String(255), unique=True)
    location = Column(String(255))
    refund_policy = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    images = Column(Text, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    coordinates = Column(String(255))
    user_id = Column(Integer, nullable=False)
    country_id = Column(Integer, nullable=False)
    region_id = Column(Integer, nullable=False)
    event_category_id = Column(Integer, nullable=False)
    # event_category = relationship('EventCategory', back_populates='events')
    pricing = Column(String, default='paid', nullable=False)
    floor_plan = Column(Text)
    status = Column(String(255), nullable=False)
    reviewed_by = Column(String(255))
    service_charge = Column(Numeric(10, 2))

    def __init__(self, name, location, refund_policy, description, images, start_date, end_date, start_time, end_time,
                 coordinates, user_id, country_id, region_id, event_category_id, pricing, floor_plan, status,
                 reviewed_by, service_charge, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.location = location
        self.refund_policy = refund_policy
        self.description = description
        self.images = images
        self.start_date = start_date
        self.end_date = end_date
        self.start_time = start_time
        self.end_date = end_date
        self.coordinates = coordinates
        self.user_id = user_id
        self.country_id = country_id
        self.region_id = region_id
        self.event_category_id = event_category_id
        self.pricing = pricing
        self.floor_plan = floor_plan
        self.end_time = end_time
        self.status = status
        self.reviewed_by = reviewed_by
        self.service_charge = service_charge
