#!/usr/bin/env python
"""
The orders module defines the order model/entity.
"""
from sqlalchemy import Column, String, Integer, Numeric, BigInteger, TIMESTAMP, Text

from models.basemodel import BaseModel, Base


class Order(BaseModel, Base):
    """
    The Order model defines the order entity.
    
    :param user_id: The ID of the user who made the order.
    :param ticket_id: The ID of the purchased ticket.
    :param quantity: The quantity of tickets ordered.
    :param price: The total price of the order.
    :param reference: The reference number for the order.
    :param other_details: Additional details related to the order.
    :param ticket_type: The type of the ticket.
    :param currency: The currency used for the order.
    :param payment_status: The status of the payment (e.g., pending, completed).
    :param qr_code: The QR code associated with the order.
    :param delivery_status: The status of the delivery (e.g., pending, delivered).
    :param delivery_info: Information about the delivery.
    :param tickets_left: The number of tickets remaining for the event.
    :param admission_details: Details regarding admission.
    :param created_at: The timestamp when the order was created.
    :param updated_at: The timestamp when the order was last updated.
    :param deleted_at: The timestamp when the order was deleted (soft delete).
    :param myghpay_session_code: Session code for the payment.
    :param discount_info: Information about any discounts applied.
    :param discount_amount: The amount of discount applied to the order.
    :param chale_service_charge: The service charge for the order.
    """

    __tablename__ = 'orders'

    user_id = Column(BigInteger, nullable=False)
    ticket_id = Column(BigInteger, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(8, 2), nullable=False)
    reference = Column(String(255), nullable=True)
    other_details = Column(Text, nullable=True)
    ticket_type = Column(String(255), nullable=False)
    currency = Column(String(255), nullable=False)
    payment_status = Column(String(255), default='pending', nullable=False)
    qr_code = Column(String(255), nullable=False)
    delivery_status = Column(String(255), default='pending', nullable=False)
    delivery_info = Column(Text, nullable=True)
    tickets_left = Column(Integer, default=1, nullable=False)
    admission_details = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)
    deleted_at = Column(TIMESTAMP, nullable=True)
    myghpay_session_code = Column(Text, nullable=True)
    discount_info = Column(Text, nullable=True)
    discount_amount = Column(Numeric(10, 2), default=0.00, nullable=True)
    chale_service_charge = Column(Numeric(10, 2), default=0.00, nullable=True)

    # # Define relationships if necessary
    # user = relationship('User', back_populates='orders')  # Assuming User model has 'orders' relationship
    # ticket = relationship('Ticket', back_populates='orders')  # Assuming Ticket model has 'orders' relationship

    def __init__(self, user_id, ticket_id, quantity, price, ticket_type, currency, qr_code,
                 payment_status='pending', delivery_status='pending', tickets_left=1,
                 reference=None, other_details=None, delivery_info=None, admission_details=None,
                 created_at=None, updated_at=None, deleted_at=None, myghpay_session_code=None,
                 discount_info=None, discount_amount=0.00, chale_service_charge=0.00, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.ticket_id = ticket_id
        self.quantity = quantity
        self.price = price
        self.reference = reference
        self.other_details = other_details
        self.ticket_type = ticket_type
        self.currency = currency
        self.payment_status = payment_status
        self.qr_code = qr_code
        self.delivery_status = delivery_status
        self.delivery_info = delivery_info
        self.tickets_left = tickets_left
        self.admission_details = admission_details
        self.created_at = created_at
        self.updated_at = updated_at
        self.deleted_at = deleted_at
        self.myghpay_session_code = myghpay_session_code
        self.discount_info = discount_info
        self.discount_amount = discount_amount
        self.chale_service_charge = chale_service_charge
