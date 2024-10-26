#!/usr/bin/env python
"""
The tickets module defines the ticket model/entity.
"""
from sqlalchemy import Column, String, Integer, Text, BigInteger

from models.basemodel import BaseModel, Base


class Ticket(BaseModel, Base):
    """
    The Ticket model defines the ticket entity.
    
    :param title: The title of the ticket.
    :param description: A detailed description of the ticket.
    :param quantity: The total number of tickets available.
    :param image: A URL or path to an image associated with the ticket.
    :param price: The price of the ticket.
    :param entries_allowed_per_ticket: The number of entries allowed per ticket.
    :param event_id: The ID of the associated event.
    :param tour_id: The ID of the associated tour (if applicable).
    :param created_at: The timestamp when the ticket was created.
    :param updated_at: The timestamp when the ticket was last updated.
    :param deleted_at: The timestamp when the ticket was deleted (soft delete).
    """

    __tablename__ = 'tickets'

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    quantity = Column(Integer, nullable=False)
    image = Column(Text, nullable=True)
    price = Column(Integer, nullable=False)
    entries_allowed_per_ticket = Column(Integer, default=1, nullable=False)
    event_id = Column(BigInteger, nullable=True)
    tour_id = Column(BigInteger, nullable=True)

    def __init__(self, title, quantity, price, entries_allowed_per_ticket, event_id=None, tour_id=None,
                 description=None, image=None, created_at=None, updated_at=None, deleted_at=None, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.description = description
        self.quantity = quantity
        self.image = image
        self.price = price
        self.entries_allowed_per_ticket = entries_allowed_per_ticket
        self.event_id = event_id
        self.tour_id = tour_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.deleted_at = deleted_at
